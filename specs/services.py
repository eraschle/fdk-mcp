"""
Service Layer für 3D Modellsucher App
"""

import asyncio
import concurrent.futures
import glob
import os
import threading
from datetime import datetime, timedelta
from typing import Callable, Any
import subprocess
import json

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from PIL import Image, ImageTk

from models import ImageFile, SearchResult, AppConfig, CacheItem, FDKObject


class FileSearchService:
    """Service for file system operations and search"""

    def __init__(self, config: AppConfig):
        self.config = config
        self._search_cancelled = False

    def search_images(
        self,
        base_path: str,
        progress_callback: Callable[[int, str], None] | None = None,
    ) -> SearchResult:
        """Search for images in directory structure"""
        if not os.path.isdir(base_path):
            raise ValueError(f"Directory does not exist: {base_path}")

        self._search_cancelled = False
        search_start = datetime.now()

        # Build search patterns
        patterns = []
        for fmt in self.config.supported_formats:
            patterns.append(os.path.join(base_path, "**", f"*OBJ_{fmt}"))

        # Collect all matching files
        all_files = []
        for i, pattern in enumerate(patterns):
            if self._search_cancelled:
                break

            pattern_files = glob.glob(pattern, recursive=True)
            all_files.extend(pattern_files)

            if progress_callback:
                progress_callback(len(all_files), f"Suche Pattern {i + 1}/{len(patterns)}")

        if self._search_cancelled:
            return SearchResult({}, 0, base_path, search_start)

        # Group files by object folder
        images_by_object = {}
        for i, file_path in enumerate(all_files):
            if self._search_cancelled:
                break

            image_file = ImageFile.from_path(file_path, base_path)

            if image_file.object_folder not in images_by_object:
                images_by_object[image_file.object_folder] = []

            images_by_object[image_file.object_folder].append(image_file)

            if progress_callback and (i + 1) % 10 == 0:
                progress_callback(i + 1, f"Verarbeitet: {i + 1}/{len(all_files)}")

        return SearchResult(
            images_by_object=images_by_object,
            total_count=len(all_files),
            search_path=base_path,
            search_time=search_start,
        )

    def get_fachbereiche(self, base_path: str) -> list[str]:
        """Get list of Fachbereiche (subdirectories) in base path"""
        if not os.path.isdir(base_path):
            return []

        try:
            return sorted(
                [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
            )
        except Exception:
            return []

    def cancel_search(self):
        """Cancel ongoing search operation"""
        self._search_cancelled = True

    @staticmethod
    def open_file_location(file_path: str):
        """Open file location in system explorer"""
        try:
            directory = os.path.dirname(os.path.abspath(file_path))
            if not os.path.exists(directory):
                print(f"Directory does not exist: {directory}")
                return

            # Use /select to highlight the specific file in Explorer
            subprocess.run(["explorer", "/select,", os.path.abspath(file_path)], check=False)
        except Exception as e:
            print(f"Error opening explorer for {file_path}: {e}")
            # Fallback: try to open just the directory
            try:
                directory = os.path.dirname(os.path.abspath(file_path))
                subprocess.run(["explorer", directory], check=False)
            except Exception as fallback_error:
                print(f"Fallback also failed: {fallback_error}")


class CacheService:
    """LRU Cache service for images"""

    def __init__(self, max_size: int = 500):
        self.max_size = max_size
        self._cache: dict[str, CacheItem] = {}
        self._lock = threading.Lock()

    def get(self, file_path: str) -> CacheItem | None:
        """Get cached item and update access time"""
        with self._lock:
            if file_path in self._cache:
                item = self._cache[file_path]
                item.access_time = datetime.now()
                return item
            return None

    def set(self, file_path: str, image_file: ImageFile, image_data: Any):
        """Cache image data with LRU eviction"""
        with self._lock:
            now = datetime.now()

            # Remove oldest items if cache is full
            while len(self._cache) >= self.max_size:
                oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].access_time)
                del self._cache[oldest_key]

            # Add new item
            self._cache[file_path] = CacheItem(
                image_file=image_file,
                image_data=image_data,
                access_time=now,
                load_time=now,
            )

    def clear(self):
        """Clear all cached items"""
        with self._lock:
            self._cache.clear()

    def size(self) -> int:
        """Get current cache size"""
        with self._lock:
            return len(self._cache)

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hit_rate": 0.0,  # Could be implemented with hit/miss counters
            }


class ImageProcessingService:
    """Service for image processing and loading"""

    def __init__(self, config: AppConfig, cache_service: CacheService):
        self.config = config
        self.cache_service = cache_service
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=config.max_workers)
        self.loop = None

    def set_event_loop(self, loop):
        """Set asyncio event loop"""
        self.loop = loop

    async def load_image_async(self, image_file: ImageFile) -> tuple[str, Any]:
        """Load image asynchronously"""
        if self.loop is None:
            self.loop = asyncio.get_event_loop()

        # Check cache first
        cached_item = self.cache_service.get(image_file.path)
        if cached_item:
            return image_file.name, cached_item.image_data

        try:
            # Process image in thread pool
            future = self.loop.run_in_executor(self.executor, self._process_image, image_file)
            image_data = await future

            # Cache the result
            self.cache_service.set(image_file.path, image_file, image_data)

            return image_file.name, image_data

        except Exception as e:
            print(f"Error loading image {image_file.path}: {e}")
            # Return placeholder on error
            placeholder = ImageTk.PhotoImage(Image.new("RGB", self.config.image_size, color="red"))
            return image_file.name, placeholder

    def _process_image(self, image_file: ImageFile) -> ImageTk.PhotoImage:
        """Process image in background thread"""
        try:
            with Image.open(image_file.path) as img:
                # Store original dimensions in image_file if not set
                if image_file.dimensions is None:
                    image_file.dimensions = img.size

                # Create thumbnail
                img.thumbnail(self.config.image_size, Image.Resampling.LANCZOS)

                # Create fixed-size canvas and center the image
                canvas = Image.new("RGBA", self.config.image_size, color=(255, 255, 255, 0))
                x = (self.config.image_size[0] - img.width) // 2
                y = (self.config.image_size[1] - img.height) // 2
                canvas.paste(img, (x, y))

                return ImageTk.PhotoImage(canvas)

        except Exception as e:
            print(f"Error processing image {image_file.path}: {e}")
            return ImageTk.PhotoImage(Image.new("RGB", self.config.image_size, color="lightgray"))

    def load_image_sync(self, image_file: ImageFile) -> tuple[str, Any]:
        """Load image synchronously (fallback)"""
        # Check cache first
        cached_item = self.cache_service.get(image_file.path)
        if cached_item:
            return image_file.name, cached_item.image_data

        # Process and cache
        image_data = self._process_image(image_file)
        self.cache_service.set(image_file.path, image_file, image_data)

        return image_file.name, image_data

    async def load_images_batch(
        self,
        image_files: list[ImageFile],
        progress_callback: Callable[[int, int, ImageFile, Any], None] | None = None,
    ):
        """Load multiple images asynchronously with progress updates"""
        tasks = []

        for image_file in image_files:
            # Check cache first
            cached_item = self.cache_service.get(image_file.path)
            if cached_item:
                if progress_callback:
                    progress_callback(
                        len(tasks) + 1,
                        len(image_files),
                        image_file,
                        cached_item.image_data,
                    )
                continue

            # Create async task for uncached images
            task = asyncio.create_task(self.load_image_async(image_file))
            tasks.append((image_file, task))

        # Process tasks
        for i, (image_file, task) in enumerate(tasks):
            try:
                _, image_data = await task

                if progress_callback:
                    progress_callback(i + 1, len(tasks), image_file, image_data)

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in batch loading: {e}")

    def create_placeholder_image(self) -> Any:
        """Create placeholder image"""
        placeholder_img = Image.new("RGB", self.config.image_size, color="white")

        # Add border and text
        from PIL import ImageDraw

        draw = ImageDraw.Draw(placeholder_img)
        w, h = self.config.image_size
        draw.rectangle([0, 0, w - 1, h - 1], outline="lightgray", width=2)
        draw.text((w // 2, h // 2), "Lädt...", fill="gray", anchor="mm")

        return ImageTk.PhotoImage(placeholder_img)

    def shutdown(self):
        """Shutdown the thread pool"""
        self.executor.shutdown(wait=True)


class ConfigurationService:
    """Service for application configuration"""

    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self._config = AppConfig()

    def load_config(self) -> AppConfig:
        """Load configuration from file"""
        try:
            import json

            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Update config with loaded values
                    for key, value in data.items():
                        if hasattr(self._config, key):
                            setattr(self._config, key, value)
        except Exception as e:
            print(f"Error loading config: {e}")

        return self._config

    def save_config(self, config: AppConfig):
        """Save configuration to file"""
        try:
            import json

            data = {
                "cache_size": config.cache_size,
                "max_workers": config.max_workers,
                "image_size": config.image_size,
                "window_size": config.window_size,
                "default_path": config.default_path,
                "supported_formats": config.supported_formats,
                "enable_api_panel": config.enable_api_panel,
                "api_base_url": config.api_base_url,
                "api_language": config.api_language,
                "api_cache_ttl": config.api_cache_ttl,
                "api_timeout": config.api_timeout,
                "api_panel_width": config.api_panel_width,
                "api_sash_position": config.api_sash_position,
            }

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"Error saving config: {e}")

    def get_config(self) -> AppConfig:
        """Get current configuration"""
        return self._config


class FDKApiService:
    """Service for SBB FDK API operations"""

    def __init__(self, config: AppConfig):
        self.config = config
        self._cache: dict[str, tuple[FDKObject, datetime]] = {}
        self._cache_lock = threading.Lock()

        # Configure session with connection pooling and retry strategy
        self.session = requests.Session()
        # Note: timeout is set per request, not on session

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504],
        )

        # Configure HTTP adapter with connection pooling
        adapter = HTTPAdapter(pool_connections=10, pool_maxsize=20, max_retries=retry_strategy)

        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set headers for better performance
        self.session.headers.update(
            {
                "User-Agent": "3D-Modellsucher/1.0",
                "Accept": "application/json",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            }
        )

    def _get_fdk_objects_url(self, object_id: str) -> str:
        """Build FDK API URL for specific object"""
        url = f"{self.config.api_base_url}/objects/{object_id}"
        if self.config.api_language:
            url += f"?language={self.config.api_language}"
        return url

    def _extract_object_id_from_filename(self, filename: str) -> str | None:
        """Extract FDK object ID from image filename (e.g., OBJ_BR_1_xxx.png -> OBJ_BR_1)"""
        try:
            base_name = os.path.splitext(filename)[0]
            parts = base_name.split("_")

            # Look for pattern: OBJ_XX_Y where XX is letters and Y is number
            if len(parts) >= 3 and parts[0] == "OBJ":
                # Return OBJ_XX_Y format
                return f"{parts[0]}_{parts[1]}_{parts[2]}"
        except Exception:
            pass
        return None

    def _is_cache_valid(self, cached_time: datetime) -> bool:
        """Check if cached data is still valid"""
        return datetime.now() - cached_time < timedelta(seconds=self.config.api_cache_ttl)

    def _get_cached_object(self, object_id: str) -> FDKObject | None:
        """Get cached FDK object if valid"""
        with self._cache_lock:
            if object_id in self._cache:
                fdk_object, cached_time = self._cache[object_id]
                if self._is_cache_valid(cached_time):
                    return fdk_object
                else:
                    # Remove expired cache entry
                    del self._cache[object_id]
        return None

    def _cache_object(self, object_id: str, fdk_object: FDKObject):
        """Cache FDK object with timestamp"""
        with self._cache_lock:
            self._cache[object_id] = (fdk_object, datetime.now())

    def _make_api_request(self, object_id: str) -> dict | None:
        """Make HTTP request to FDK API"""
        try:
            url = self._get_fdk_objects_url(object_id)
            response = self.session.get(url, timeout=self.config.api_timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API request failed for {object_id}: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Failed to parse API response for {object_id}: {e}")
            return None

    async def get_fdk_object_async(self, object_id: str) -> FDKObject | None:
        """Get FDK object asynchronously with caching"""
        # Check cache first
        cached_object = self._get_cached_object(object_id)
        if cached_object:
            return cached_object

        # Make API request in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        try:
            api_data = await loop.run_in_executor(None, self._make_api_request, object_id)

            if api_data and "error" not in api_data:
                fdk_object = FDKObject.from_api_response(api_data)
                self._cache_object(object_id, fdk_object)
                return fdk_object
            else:
                print(f"API returned error or no data for {object_id}")
                return None

        except Exception as e:
            print(f"Error getting FDK object {object_id}: {e}")
            return None

    def get_fdk_object_for_image(self, image_file: ImageFile) -> FDKObject | None:
        """Get FDK object for an image file synchronously"""
        object_id = self._extract_object_id_from_filename(image_file.name)
        if not object_id:
            return None

        # Check cache first
        cached_object = self._get_cached_object(object_id)
        if cached_object:
            return cached_object

        # Make synchronous request
        api_data = self._make_api_request(object_id)
        if api_data and "error" not in api_data:
            fdk_object = FDKObject.from_api_response(api_data)
            self._cache_object(object_id, fdk_object)
            return fdk_object

        return None

    async def get_fdk_object_for_image_async(self, image_file: ImageFile) -> FDKObject | None:
        """Get FDK object for an image file asynchronously"""
        object_id = self._extract_object_id_from_filename(image_file.name)
        if not object_id:
            return None

        return await self.get_fdk_object_async(object_id)

    def does_fdk_object_exist(self, object_id: str) -> bool:
        """Check if FDK object exists in API"""
        try:
            url = self._get_fdk_objects_url(object_id)
            response = self.session.head(url, timeout=self.config.api_timeout)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def clear_cache(self):
        """Clear all cached FDK objects"""
        with self._cache_lock:
            self._cache.clear()

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        with self._cache_lock:
            valid_entries = 0
            for _, (_, cached_time) in self._cache.items():
                if self._is_cache_valid(cached_time):
                    valid_entries += 1

            return {
                "total_entries": len(self._cache),
                "valid_entries": valid_entries,
                "expired_entries": len(self._cache) - valid_entries,
                "cache_ttl": self.config.api_cache_ttl,
            }

    def cleanup_expired_cache(self):
        """Remove expired cache entries"""
        with self._cache_lock:
            expired_keys = []
            for object_id, (_, cached_time) in self._cache.items():
                if not self._is_cache_valid(cached_time):
                    expired_keys.append(object_id)

            for key in expired_keys:
                del self._cache[key]

            return len(expired_keys)

    def close(self):
        """Close the requests session"""
        self.session.close()

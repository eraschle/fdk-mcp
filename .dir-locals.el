;;; Directory Local Variables            -*- no-byte-compile: t -*-
;;; For more information see (info "(emacs) Directory Variables")

((nil . ((jinx-dir-local-words . "aksCode assemblyRelationships componentRelationships domainModel ebkpConcepts ifcClass ifcClassAssignments nameObjectGroup nameSubgroup propertySet propertySets")))
 (python-mode . ((eval . (unless
                             (s-contains-p "/home/elyo/workspace/elyo/fdk-mcp/.venv/bin/" (getenv "PATH"))
                           (setenv "PATH"
                                   (concat "/home/elyo/workspace/elyo/fdk-mcp/.venv/bin/" path-separator
                                           (getenv "PATH")))))
                 (eval . (setenv "VIRTUALENV" "/home/elyo/workspace/elyo/fdk-mcp/.venv/"))
                 (eval . (setenv "PYTHONPATH"
                                 (string-join
                                  (seq-filter (lambda (dir) (not (string-blank-p dir)))
                                              (seq-uniq
                                               (append (list "/home/elyo/workspace/elyo/fdk-mcp/src/")
                                                       (when-let ((existing (getenv "PYTHONPATH")))
                                                         (string-split existing path-separator)))))
                                  path-separator))))))

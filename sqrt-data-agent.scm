;; [[file:org/core-new.org::*Guix module][Guix module:1]]
(define-module (sqrt-data)
  #:use-module (srfi srfi-1)
  #:use-module (srfi srfi-26)
  #:use-module (ice-9 match)
  #:use-module (ice-9 rdelim)
  #:use-module (ice-9 popen)
  #:use-module (guix download)
  #:use-module (guix git-download)
  #:use-module (guix gexp)
  #:use-module (guix packages)
  #:use-module (guix build utils)
  #:use-module (guix build-system python)
  #:use-module (guix build-system gnu)
  #:use-module ((guix licenses) #:prefix license:)
  #:use-module (gnu packages admin)
  #:use-module (gnu packages base)
  #:use-module (gnu packages compression)
  #:use-module (gnu packages databases)
  #:use-module (gnu packages gawk)
  #:use-module (gnu packages gnome)
  #:use-module (gnu packages mpd)
  #:use-module (gnu packages networking)
  #:use-module (gnu packages rsync)
  #:use-module (gnu packages python-web)
  #:use-module (gnu packages python-xyz)
  #:use-module (gnu packages python-science)
  #:use-module (gnu packages ssh)
  #:use-module (gnu packages version-control))
;; Guix module:1 ends here

;; [[file:org/core-new.org::*Guix module][Guix module:2]]
(define %source-dir (dirname (current-filename)))
;; (define %source-dir "/home/pavel/Code/self-quantification/sqrt-data/")
;; Guix module:2 ends here

;; [[file:org/core-new.org::*Guix module][Guix module:3]]
(define git-file?
  (let* ((pipe (with-directory-excursion %source-dir
                 (open-pipe* OPEN_READ "git" "ls-files")))
         (files (let loop ((lines '()))
                  (match (read-line pipe)
                    ((? eof-object?)
                     (reverse lines))
                    (line
                     (loop (cons line lines))))))
         (status (close-pipe pipe)))
    (lambda (file stat)
      (match (stat:type stat)
        ('directory
         #t)
        ((or 'regular 'symlink)
         (any (cut string-suffix? <> file) files))
        (_
         #f)))))
;; Guix module:3 ends here

;; [[file:org/core-new.org::*Guix module][Guix module:4]]
(define (git-version)
  (let* ((pipe (with-directory-excursion %source-dir
                 (open-pipe* OPEN_READ "git" "describe" "--always" "--tags")))
         (version (read-line pipe)))
    (close-pipe pipe)
    version))
;; Guix module:4 ends here

;; [[file:org/core-new.org::*Guix module][Guix module:5]]
(define-public osync
  (package
    (name "osync")
    (version "1.3-beta3")
    (source
     (origin
       (method git-fetch)
       (uri (git-reference
             (url "https://github.com/deajan/osync/")
             (commit (string-append "v" version))))
       (file-name (git-file-name name version))
       (sha256
        (base32 "1zpxypgfj6sr87wq6s237fr2pxkncjb0w9hq14zfjppkvws66n0w"))))
    (build-system gnu-build-system)
    (arguments
     `(#:tests? #f
       #:validate-runpath? #f
       #:phases
       (modify-phases %standard-phases
         (add-after 'unpack 'patch-file-names
           (lambda _
             ;; Silence beta warining. Otherwise the exitcode is not zero
             (substitute* "osync.sh" (("IS_STABLE=false") "IS_STABLE=true"))))
         (delete 'bootstrap)
         (delete 'configure)
         (delete 'build)
         (replace 'install
           (lambda* (#:key outputs #:allow-other-keys)
             (let ((out (string-append (assoc-ref outputs "out"))))
               ;; Use system* because installer returns exitcode 2 because it doesn't find systemd or initrc
               (system* "./install.sh" (string-append "--prefix=" out) "--no-stats")
               (mkdir (string-append out "/bin"))
               (symlink (string-append out "/usr/local/bin/osync.sh")
                        (string-append out "/bin/osync.sh"))
               (symlink (string-append out "/usr/local/bin/osync-batch.sh")
                        (string-append out "/bin/osync-batch.sh"))
               (symlink (string-append out "/usr/local/bin/ssh-filter.sh")
                        (string-append out "/bin/ssh-filter.sh"))
               #t))))))
    ;; TODO replace the executables with full paths
    ;; XXX Can't put "iputils" in propagated-inputs because on Guix
    ;; "ping" is in setuid-programs. Set "REMOTE_HOST_PING" to false if ping
    ;; is not available.
    (propagated-inputs
     `(("rsync" ,rsync)
       ("gawk" ,gawk)
       ("coreutils" ,coreutils)
       ("openssh" ,openssh)
       ("gzip" ,gzip)
       ("hostname" ,inetutils)))
    (synopsis "A robust two way (bidirectional) file sync script based on rsync with fault tolerance, POSIX ACL support, time control and near realtime sync")
    (home-page "http://www.netpower.fr/osync")
    (license license:bsd-3)
    (description "A two way filesync script running on bash Linux, BSD, Android, MacOSX, Cygwin, MSYS2, Win10 bash and virtually any system supporting bash). File synchronization is bidirectional, and can be run manually, as scheduled task, or triggered on file changes in daemon mode. It is a command line tool rsync wrapper with a lot of additional features baked in.")))
;; Guix module:5 ends here

;; [[file:org/core-new.org::*Guix module][Guix module:6]]
(define-public sqrt-data-agent
  (package
    (name "sqrt-data-agent")
    (version (git-version))
    (source
     (local-file %source-dir #:recursive? #t #:select? git-file?))
    (build-system python-build-system)
    (arguments
     `(#:tests? #f
       #:phases
       (modify-phases %standard-phases
         (add-before 'build 'fix-dependencies
           (lambda _
             (substitute* "sqrt_data_agent/sync.py"
               (("EXEC_NOTIFY_SEND = (.*)")
                (format #f "EXEC_NOTIFY_SEND = ~s\n" (which "notify-send"))))
             (substitute* "sqrt_data_agent/sync.py"
               (("EXEC_OSYNC = (.*)")
                (format #f "EXEC_OSYNC = ~s\n" (which "osync.sh")))))))))
    (native-inputs
     `(("git" ,git-minimal)))
    (inputs
     `(("libnotify" ,libnotify)
       ("osync" ,osync)))
    (propagated-inputs
     `(("python-pandas" ,python-pandas)
       ("python-numpy" ,python-numpy)
       ("python-mpd2" ,python-mpd2)
       ("python-requests" ,python-requests)
       ("python-furl" ,python-furl)
       ("dynaconf" ,dynaconf)))
    (synopsis "Agent for sqrt-data")
    (description "Agent for sqrt-data")
    (home-page "https://github.com/SqrtMinusOne/sqrt-data")
    (license license:gpl3)))
;; Guix module:6 ends here

;; [[file:org/core-new.org::*Guix module][Guix module:7]]
sqrt-data-agent
;; Guix module:7 ends here

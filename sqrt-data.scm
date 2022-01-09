;; [[file:org/core.org::*Guix module][Guix module:1]]
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

;; [[file:org/core.org::*Guix module][Guix module:2]]
(define %source-dir (dirname (current-filename)))
;; (define %source-dir "/home/pavel/Code/self-quantification/sqrt-data/")
;; Guix module:2 ends here

;; [[file:org/core.org::*Guix module][Guix module:3]]
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

;; [[file:org/core.org::*Guix module][Guix module:4]]
(define (git-version)
  (let* ((pipe (with-directory-excursion %source-dir
                 (open-pipe* OPEN_READ "git" "describe" "--always" "--tags")))
         (version (read-line pipe)))
    (close-pipe pipe)
    version))
;; Guix module:4 ends here

;; [[file:org/core.org::*Guix module][Guix module:5]]
(define-public python-readchar
  (package
    (name "python-readchar")
    (version "3.0.5")
    (source
     (origin
       (method url-fetch)
       (uri (pypi-uri "readchar" version))
       (sha256
        (base32 "1h42qjj9079yv19rd1zdl3wg915bg2wrvfjzd4xpyyy3k0gbgxfi"))))
    (arguments
     `(#:tests? #f))
    (build-system python-build-system)
    (propagated-inputs (list python-flake8))
    (home-page "https://github.com/magmax/python-readchar")
    (synopsis "Utilities to read single characters and key-strokes")
    (description "Utilities to read single characters and key-strokes")
    (license license:expat)))

(define-public python-blessed-1.19
  (package
    (inherit python-blessed)
    (version "1.19.0")
    (source
     (origin
       (method url-fetch)
       (uri (pypi-uri "blessed" version))
       (sha256
        (base32 "0qbsmnjwj016a0zg0jx9nnbfkzr700jlms18nlqa7bk1ax7gkc2d"))
       (modules '((guix build utils)))
       (snippet
        '(begin
           ;; Don't get hung up on Windows test failures.
           (delete-file "blessed/win_terminal.py") #t))))))

(define-public python-inquirer
  (package
    (name "python-inquirer")
    (version "2.9.1")
    (source
     (origin
       (method url-fetch)
       (uri (pypi-uri "inquirer" version))
       (sha256
        (base32 "0pdzkm52dz9fy67qpgivq99hfw5j5f3ry73pcpndgaxwm3maiw35"))))
    (build-system python-build-system)
    (propagated-inputs (list python-blessed-1.19 python-editor python-readchar))
    (arguments
     `(#:tests? #f))
    (home-page "https://github.com/magmax/python-inquirer")
    (synopsis
     "Collection of common interactive command line user interfaces, based on Inquirer.js")
    (description
     "Collection of common interactive command line user interfaces, based on
Inquirer.js")
    (license license:expat)))

(define-public python-sqlitedict
  (package
    (name "python-sqlitedict")
    (version "1.7.0")
    (source
     (origin
       (method url-fetch)
       (uri (pypi-uri "sqlitedict" version))
       (sha256
        (base32 "0mmdph6yrlynyyc88hdg0m12k4p3ppn029k925sxmm5c38qcrzra"))))
    (build-system python-build-system)
    (home-page "https://github.com/piskvorky/sqlitedict")
    (synopsis
     "Persistent dict in Python, backed up by sqlite3 and pickle, multithread-safe.")
    (description
     "Persistent dict in Python, backed up by sqlite3 and pickle, multithread-safe.")
    (license license:asl2.0)))
;; Guix module:5 ends here

;; [[file:org/core.org::*Guix module][Guix module:6]]
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
;; Guix module:6 ends here

;; [[file:org/core.org::*Guix module][Guix module:7]]
(define-public sqrt-data
  (package
    (name "sqrt-data")
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
             (substitute* "setup.py" (("psycopg2-binary") "psycopg2"))
             (substitute* "sqrt_data/service/sync.py"
               (("EXEC_NOTIFY_SEND = (.*)")
                (format #f "EXEC_NOTIFY_SEND = ~s\n" (which "notify-send"))))
             (substitute* "sqrt_data/service/sync.py"
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
       ("python-click" ,python-click)
       ("python-inquirer", python-inquirer)
       ("python-mpd2" ,python-mpd2)
       ("python-sqlalchemy" ,python-sqlalchemy)
       ("python-psycopg2" ,python-psycopg2)
       ("python-requests" ,python-requests)
       ("python-tqdm" ,python-tqdm)
       ("python-beautifulsoup4" ,python-beautifulsoup4)
       ("python-furl" ,python-furl)
       ("python-sqlitedict" ,python-sqlitedict)
       ("python-schedule" ,python-schedule)
       ("dynaconf" ,dynaconf)))
    (synopsis "My self-quantification scripts")
    (description "My self-quantification scripts")
    (home-page "https://github.com/SqrtMinusOne/sqrt-data")
    (license license:gpl3)))
;; Guix module:7 ends here

;; [[file:org/core.org::*Guix module][Guix module:8]]
sqrt-data
;; Guix module:8 ends here

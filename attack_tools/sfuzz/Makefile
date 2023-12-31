# This file was automatically built by the simple fuzzer configuration process
# Manual edits will not be saved if you run configure again
# you have been warned.

### Variables for building
MKTEMP=/usr/bin/mktemp
CCPATH=/usr/bin
CC=gcc
AR=/usr/bin/ar
FIND=/usr/bin/find
TAR=/usr/bin/tar
MAINT= <>
ARCH=x86_64
XARGS=/usr/bin/xargs
VERSION=0.7.0
MD5SUM=/usr/bin/md5sum
INSTALL=/usr/bin/install
INSTALL_DIR=/usr/bin/install -d
CFLAGS=-g -O2 -Wall -I. -DPREFIX=\"/usr/local\" -D_GNU_SOURCE -fPIC -rdynamic -DHAVE_MEMMEM=1  
LDFLAGS=
TARGET_PLAT=Linux
CP=/usr/bin/cp
SED=/usr/bin/sed
CAT=/usr/bin/cat
UNAME=/usr/bin/uname
DIRNAME=/usr/bin/dirname
BASENAME=/usr/bin/basename
LS=/usr/bin/ls
GREP=/usr/bin/grep
PREFIX=/usr/local
RM=/usr/bin/rm
MKDIR=/usr/bin/mkdir
SHARED_INC=
SHARED_OPTS= -shared -rdynamic

SF_OBJS=file-utils.o sfuzz.o os-abs.o sfo_interface.o
SNOOP_OBJS=snoop.o os-abs.o
SFO_OBJS=sfuzz_oracle.o  sfuzz_oracle_ptrace.o
PLUGIN_EXAMPLE_OBJS=sfuzz-plugin-example.o sfuzz-plugin-ssl-transport.o sfuzz-server-plugin.o

LIBS= -ldl

BIN_DIR=/usr/local/bin/
SHARE_DIR=/usr/local/share/
SFUZZ_SAMPLE=sfuzz-sample/

PROGS=sfuzz sfo sfuzz-plugin-example.so sfuzz-server-plugin.so 

all: sfuzz sfo sfuzz-plugin-example.so sfuzz-server-plugin.so 
	@echo Finished building.

.PHONY: all install uninstall clean dist-clean distclean release

sfuzz sfuzz.exe: $(SF_OBJS)
	@echo "[LINK] $@"
	@$(CCPATH)/$(CC) -o $@ $(SF_OBJS) $(LDFLAGS) $(LIBS)

snoop snoop.exe: $(SNOOP_OBJS)
	@echo "[LINK] $@"
	@$(CCPATH)/$(CC) -o $@ $(SNOOP_OBJS) $(LDFLAGS) $(LIBS)

sfo sfo.exe: $(SFO_OBJS)
	@echo "[LINK] $@"
	@$(CCPATH)/$(CC) -o $@ $(SFO_OBJS) $(LDFLAGS) $(LIBS)

%.so: %.c $(SHARED_INC)
	@echo "[LINK] $@"
	@$(CCPATH)/$(CC) $(CFLAGS) -D__PLUGIN_BUILD__ -o $@ $< $(SHARED_INC) $(SHARED_OPTS)

-include $(SF_OBJS:.o=.d)
-include $(SNOOP_OBJS:.o=.d)

%.o: %.c
	@echo "[CC] $@"
	@$(CCPATH)/$(CC) $(CFLAGS) -MT '$@' -MT '$*.d' -MD -c $<
	@$(CCPATH)/$(CC) -c -o $@ $(CFLAGS) $<

install: all
	@echo "Installing to: $(DESTDIR)$(PREFIX)"
	@$(INSTALL_DIR) $(DESTDIR)$(BIN_DIR)
	@$(INSTALL) sfuzz $(DESTDIR)$(BIN_DIR)
	@$(INSTALL) sfo   $(DESTDIR)$(BIN_DIR)
	@$(INSTALL_DIR) $(DESTDIR)$(SHARE_DIR)sfuzz-db
	@$(INSTALL) $(SFUZZ_SAMPLE)* $(DESTDIR)$(SHARE_DIR)sfuzz-db
	@$(INSTALL) *.so $(DESTDIR)$(SHARE_DIR)sfuzz-db
	@echo Installed.

uninstall:
	@$(RM) -rf $(SHARE_DIR)sfuzz-db
	@$(RM) -f  $(BIN_DIR)sfuzz
	@$(RM) -f  $(BIN_DIR)sfo
	@$(RM) -f  $(BIN_DIR)sfo.exe
	@$(RM) -f  $(BIN_DIR)sfuzz.exe
	@echo "Uninstalled."

clean:
	@$(RM) -f core *~ *.o snoop snoop.exe sfuzz sfuzz.exe sfo sfo.exe *.so *.d *.deb
	@$(RM) -rf *.so.dSYM sfuzz-deb-temp

distclean dist-clean: clean
	@$(RM) -f Makefile Makefile.old
	@echo Makefile / configuration removed.

# the following is a semi-portable way of writing a debian dpkg file for
# the distribution of sfuzz as a .deb file
deb: all
	@$(MKDIR) -p -m 0700 sfuzz-deb-temp/data
	@$(MKDIR) -p -m 0700 sfuzz-deb-temp/control
	@$(MAKE) DESTDIR=sfuzz-deb-temp/data install
	@$(CP) debfile sfuzz-deb-temp/control/control
	@$(FIND) sfuzz-deb-temp/data -type f -print | $(XARGS) $(MD5SUM) > sfuzz-deb-temp/control/md5sums
	@$(SED) -ire 's@sfuzz-deb-temp/data@@g' sfuzz-deb-temp/control/md5sums
	@$(SED) -ire 's@\*@@g' sfuzz-deb-temp/control/md5sums
	@$(SED) -ire 's@VERSION@$(VERSION)@g' sfuzz-deb-temp/control/control
	@$(SED) -ire 's@ARCHITECTURE@$(ARCH)@g' sfuzz-deb-temp/control/control
	@$(SED) -ire 's@x86_64@amd64@g' sfuzz-deb-temp/control/control
	@$(SED) -ire 's/MAINTAINER/$(MAINT)/g' sfuzz-deb-temp/control/control
	@echo "2.0" > sfuzz-deb-temp/debian-binary
	@$(TAR) --owner=0 --group=0 --strip-components=2 --directory=sfuzz-deb-temp/data -czf sfuzz-deb-temp/data.tar.gz `echo $(PREFIX) | $(SED) 's@^/@@g'`
	@$(TAR) --owner=0 --group=0 --directory=sfuzz-deb-temp/control -czf sfuzz-deb-temp/control.tar.gz control md5sums
	@cd sfuzz-deb-temp && $(AR) rcs ../simple-fuzzer.deb debian-binary control.tar.gz data.tar.gz

release: distclean
	@echo Making a release tree:
	@$(RM) -rf /tmp/sfuzz-release
	@$(MKDIR) /tmp/sfuzz-release
	@$(CP) -dPar * /tmp/sfuzz-release
	@$(RM) -rf /tmp/sfuzz-release/CVS
	@$(RM) -rf /tmp/sfuzz-release/sfuzz-sample/CVS
	@$(RM) -rf /tmp/sfuzz-release/.git
	@echo /tmp/sfuzz-release is built.


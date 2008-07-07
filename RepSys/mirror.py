import sys
import os
import urlparse

from RepSys import Error, config, layout
from RepSys.svn import SVN

def mirror_url():
    mirror = config.get("global", "mirror")

def normalize_path(url):
    """normalize url for relocate_path needs"""
    parsed = urlparse.urlparse(url)
    path = os.path.normpath(parsed[2])
    newurl = urlparse.urlunparse((parsed[0], parsed[1], path,
        parsed[3], parsed[4], parsed[5]))
    return newurl

def _joinurl(url, relpath):
    parsed = urlparse.urlparse(url)
    newpath = os.path.join(parsed[2], relpath)
    newurl = urlparse.urlunparse((parsed[0], parsed[1], newpath,
        parsed[3], parsed[4], parsed[5]))
    return newurl

def same_base(parent, url):
    """returns true if parent is parent of url"""
    parent = normalize_path(parent)
    url = normalize_path(url)
    #FIXME handle paths with/without username/password
    return url.startswith(parent)

def relocate_path(oldparent, newparent, url):
    oldparent = normalize_path(oldparent)
    newparent = normalize_path(newparent)
    url = normalize_path(url)
    subpath = url[len(oldparent)+1:]
    newurl = _joinurl(newparent,  subpath) # subpath usually gets / at begining
    return newurl

def enabled(wcurl=None):
    mirror = mirror_url()
    repository = layout.repository_url()
    enabled = False
    if mirror and repository:
        enabled = True
        if wcurl and not same_base(mirror, wcurl):
            enabled = False
    return enabled

def using_on(url):
    """returnes True if the URL points to the mirror repository"""
    mirror = mirror_url()
    using = same_base(mirror, url)
    return using

def info(url, stream=sys.stderr):
    if using_on(url):
        stream.write("using mirror\n")

def mirror_relocate(oldparent, newparent, url, wcpath):
    svn = SVN()
    newurl = relocate_path(oldparent, newparent, url)
    svn.switch(newurl, url, path=wcpath, relocate="True")
    return newurl

def switchto_parent(svn, url, path):
    """Relocates the working copy to default_parent"""
    newurl = mirror_relocate(mirror_url(), layout.repository_url(), url, path)
    return newurl

def switchto_mirror(svn, url, path):
    newurl = mirror_relocate(layout.repository_url(), mirror_url(), url, path)
    return newurl

def checkout_url(url):
    mirror = mirror_url()
    default_parent = config.get("global", "default_parent")
    if mirror is not None and default_parent is not None:
        return relocate_path(default_parent, mirror, url)
    return url

def autoswitch(svn, wcpath, wcurl, newbaseurl=None):
    """Switches between mirror, default_parent, or newbaseurl"""
    nobase = False
    mirror = mirror_url()
    default_parent = config.get("global", "default_parent")
    current = default_parent
    if default_parent is None:
        raise Error, "the option default_parent from repsys.conf is "\
                "required"
    indefault = same_base(default_parent, wcurl)
    if not newbaseurl:
        if not mirror:
            raise Error, "an URL is needed when the option mirror "\
                    "from repsys.conf is not set"
        if indefault:
            chosen = mirror
        elif same_base(mirror, wcurl):
            current = mirror
            chosen = default_parent
        else:
            nobase = True
    else:
        if mirror and same_base(mirror, wcurl):
            current = mirror
        elif indefault:
            pass # !!!!
        else:
            nobase = True
        chosen = newbaseurl
    if nobase:
        raise Error, "the URL of this working copy is not based in "\
                "default_parent nor mirror URLs"
    assert current != chosen
    newurl = mirror_relocate(current, chosen, wcurl, wcpath)
    return newurl

import argparse
import sys
import os
from functools import wraps

import maya.cmds as cmds
import maya.mel as mel
import maya.standalone


def requires_standalone(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        maya.standalone.initialize(name='python')
        try:
            return f(*args, **kwargs)
        except Exception:
            raise
        finally:
            maya.standalone.uninitialize()

    return wrapper


def run(output, characters, animations, names=None):
    chars = [x for x in os.listdir(characters) if x.endswith('.fbx')]
    if names:
        chars = [x for x in chars if os.path.splitext(x)[0].lower() in names]

    characters = os.path.abspath(characters)
    characters = [os.path.join(characters, x) for x in chars]

    animations = os.path.abspath(animations)
    animations = [os.path.join(animations, x)
                  for x in os.listdir(animations) if x.endswith('.fbx')]

    return run_conversion(characters, animations, output)


@requires_standalone
def run_conversion(characters, animations, output):
    cmds.loadPlugin('fbxmaya')

    raw_dir = os.path.join(output, 'raw')
    if not os.path.isdir(raw_dir):
        os.makedirs(raw_dir)

    clean_anims = []
    clean_chars = []

    for anim in animations:
        clean_anims.append(clean(anim, raw_dir))
    for char in characters:
        clean_chars.append(clean(char, raw_dir))

    mel.eval('FBXImportCacheFile -v true')
    for char in clean_chars:
        char_name = os.path.splitext(os.path.split(char)[-1])[0]
        char_dir = output
        if not os.path.isdir(char_dir):
            os.makedirs(char_dir)
        for anim in clean_anims:
            cmds.file(new=True, force=True)
            anim_name = os.path.splitext(os.path.split(anim)[-1])[0]
            mel.eval('FBXImportMode -v add')
            cmds.file(char, i=True)
            mel.eval('FBXImportMode -v merge')
            cmds.file(anim, i=True)

            new_name = os.path.join(
                char_dir, '%s_%s.fbx' % (char_name, anim_name)
            ).replace('\\', '/')

            cmds.select(cmds.ls(type=['joint', 'transform']))
            mel.eval('FBXExport -f "%s" -s' % new_name)


def clean(path, raw_dir, do_normalize=True, height=177):
    mel.eval('FBXImportFillTimeline -v true')
    cmds.file(path, open=True, force=True, typ='FBX')

    for namespace in cmds.namespaceInfo(lon=True):

        if namespace in ['UI', 'shared']:
            continue
        try:
            cmds.namespace(removeNamespace=namespace, mnr=True)
        except Exception as e:
            print e

    new_path = os.path.join(
        raw_dir,
        os.path.split(path)[-1]
    ).replace('\\', '/')

    cmds.select(cmds.ls(type='joint'))
    [cmds.select(x, add=True) for x in cmds.ls(type='transform')
     if cmds.getAttr('%s.visibility' % x)]

    mel.eval('FBXExportCacheFile -v true')
    mel.eval('FBXExport -f "%s" -s' % new_path)
    return new_path


def main(args=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--output', '-o',
        help='Output path',
        required=True
    )
    parser.add_argument(
        '--characters', '-c',
        help='Path to the characters',
        required=True
    )
    parser.add_argument(
        '--anims', '-a',
        help='Path to the animations',
        required=True
    )
    parser.add_argument(
        '--char-names', '-n',
        nargs='*',
        help='Path to the animations'
    )

    namespace = parser.parse_args(args)
    run(
        output=namespace.output,
        characters=namespace.characters,
        animations=namespace.anims,
        names=namespace.char_names
    )


if __name__ == '__main__':
    main()

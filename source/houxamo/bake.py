import argparse
import sys
import hou
import os


OUT_NETWORK = None
BAKE_MERGE = None


def initialize_globals():
    global OUT_NETWORK, BAKE_MERGE
    OUT_NETWORK = hou.node('/out/')
    BAKE_MERGE = OUT_NETWORK.createNode('merge')


def create_fbx_bake(fbx_file, clip, agent_name, out=None):
    agent = OUT_NETWORK.createNode('agent')
    BAKE_MERGE.setNextInput(agent)
    agent.parm('source').set(2)
    agent.parm('fbxfile').set(fbx_file)
    agent.parm('fbxclipname').set(clip)
    agent.parm('inplace').set(1)
    agent.parm('fbxlocomotionnode').set('Hips')
    agent.parm('agentname').set(agent_name)
    if out:
        agent.parm('cachedir').set(out)

    return


def bake_all():
    BAKE_MERGE.parm('execute').pressButton()


def run(anims, output, scene_path=None):

    initialize_globals()

    for fpath in os.listdir(anims):
        if not fpath.endswith('.fbx'):
            continue
        _tmp = fpath.split('_')
        char = _tmp.pop(0).lower()
        clip = '_'.join(_tmp).replace(
            '(', '_').replace(')', '_').replace('.fbx', '')

        create_fbx_bake(
            fbx_file=os.path.join(anims, fpath),
            clip=clip,
            agent_name=char,
            out=output
        )

    bake_all()

    if scene_path:
        hou.hipFile.save(scene_path)


def main(args=sys.argv[1:]):

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--output', '-o',
        help='Output path',
        required=True
    )
    parser.add_argument(
        '--anims', '-a',
        help='Path to the animations',
        required=True
    )
    parser.add_argument(
        '--scene-path', '-s',
        help='(optional) Where to save the scene.'
    )

    namespace = parser.parse_args(args)
    run(namespace.anims, namespace.output, namespace.scene_path)


if __name__ == '__main__':
    main()

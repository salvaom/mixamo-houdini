# mixamo-houdini
Bridge between Mixamo animations and Houdini agents. Uses Maya to cleanup and batch process Mixamo's FBX files and Houdini to bake them into proper agents.


## Usage

### Animation attaching and cleanup (MAYA)

Download a pack from Mixamo and split the character FBX from it's animations into folders so it looks like:

```
├───anims
│       Crouch_Idle.fbx
│       Crouch_To_Standing_Idle.fbx
│       Crouch_Turn_Left_90.fbx
│       ...
├───char
│   └───mage.fbx
├───bake
└───agents
```

Execute: `mayapy mixamo-houdini/source/houxamo/clean.py -a <root>/anims -c <root>/char -o <root>/bake`


### Houdini agent bake (HOUDINI)

When all assets are clean, execute then:

`hython mixamo-houdini/source/houxamo/bake.py -a <root>/bake -o <root>/char -o <root>/agents`

# Re-Volt Blender Plugin

Blender plugin for importing and exporting cars, tracks and 3D models of the game _Re-Volt_

## Features
### Import
+ **.prm/.m**: Instances and object models
+ **.ncp**: Collision files of tracks and instances
+ **.w**: World files, including **.fob** objects and **.fin** instances and parts of the **.inf** information file
+ **parameters.txt**: Car models including parts of the car parameters

### Export
+ **.prm/.m**
+ **.ncp**: Collision files of tracks and instances
+ **.hul**

### Editing
+ Surface properties
+ Polygon properties (double-sided, translucent, ...)
+ Set object type and flags(Pick-Up, ...)
+ Set car and track properties

## Installation
Create a folder in `<blender folder>/2.XX/scripts/addons/` called `io_revolt` and copy the contents of this repository into it ([Download here](http://github.com/NiklasHassdal/io_revolt/archive/master.zip)).  

Then enable the plugin in the User Preferences: Go to Addons and search for (_Re-Volt Import/Export_).  

If you're using Linux, make sure all files and folders in your Re-Volt directory are lowercase.

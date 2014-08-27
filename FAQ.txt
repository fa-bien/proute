* How to load my data?
  First, try using the generic input plugins (PIF and PSF), by formatting your
  data for it. If the generic plugins are not generic enough for your data,
  then support must be added for it, either by asking the developer and hoping
  he has time or by adding support yourself. This is done by writing a
  plugin. User-defined plugins are python scripts; they should go to the
  "~/.proute/plugins" directory, where "~" stands for the home directory.

* How do I use the generic input plugins?
  Check the example.pif (instance file) and example.psf (solution file) in the
  sample data files. They are well documented and should be
  self-explanatory. If this is not enough, feel free to send a mail or request
  support via the website.

* How to add support for a new problem type, or for a new instance type:
  Derive the class vrpdata.VrpInputData:
  - define the defaultFor and instanceType class attributes
  - define the loadData(fName) method
  The plugins directory has several examples of how to do that.

* How to add support for a new solution type:
  Derive the class vrpdata.VrpSolutionData:
  - define the defaultFor and solutionType class attributes
  - define the loadData(fName) method
  The plugins directory is rich with examples, from simple ones (cvrp)
  to more complex ones (mcdarp).

* How to add a new visual effect:
  Derive the class style.Style:
  - define the description, parameterInfo and parameterValue class attributes
  - define the paint() method
  Examples can be found in the plugins directory, see e.g. module basestyles;
  (a bit) more documentation can be found in class style.Style.

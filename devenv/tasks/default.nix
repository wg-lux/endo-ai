{...}@inputs:
let
  endoregTasks = (
    import ./endoreg-db.nix { }
  );
  envTasks = (
    import ./env.nix { }
  );

  customTasks = {
    
  } // envTasks ;

in customTasks 
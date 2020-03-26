### Action Plugin Merge_Vars

this plugin similar to `include_vars`, but designed to merge all the variables(including dicts) in the files specified by from rather than replacing(default ansible behaviour for dicts).

This plugin is designed to support the inclusion of DRY application configuration within ansible vars. For example, if you have multiple porjects (foo, bar), and multiple environments (dev, qa, prod), and some vars are shared at various levels (project, or environment), and you want to keep your configuration DRY.

Example:

  ```
  environment/
  └── aws
      ├── cbe
      │   └── clusterid
      │       ├── app_vars.yml
      │       ├── cluster.yml
      │       └── dev_metadata.yml
      └── dev.yml
    ```

#### How to use:

```
  - name: Merge dict
    merge_vars:
        ignore_missing_files: True
        from:
        	- "test1.yml"
        	- "test2.yml"
```

where, 
	ignore_missing_files if false - raise an error, default behaviour
	from - list of files to be merged - order matters.
class DatasetFormatter:
    def __init__(self, config):
        self.renaming_mappings = config.transformation.renaming_mappings
        self.attributes_to_add = config.transformation.attributes_to_add

    def __rename_variables(self, ds):
        variables_to_remove = []
        for var in self.renaming_mappings.keys():
            if (var not in ds) and (var not in ds.coords) and (var not in ds.dims):
                print(f"WARNING: Variable '{var}' not found in dataset for renaming. Skipping...")
                variables_to_remove.append(var)

        for var in variables_to_remove:
            self.renaming_mappings.pop(var)

        return ds.rename(self.renaming_mappings)

    def __add_attributes(self, ds):
        for var, attrs in self.attributes_to_add.items():
            if var in ds.variables:
                for attr_name, attr_value in attrs.items():
                    ds[var].attrs[attr_name] = attr_value
        return ds

    def transform_data(self, datasets):
        for name, ds in datasets.items():
            ds = self.__rename_variables(ds)

            ds = self.__add_attributes(ds)

            datasets[name] = ds

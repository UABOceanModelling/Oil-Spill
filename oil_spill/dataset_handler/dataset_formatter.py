class DatasetFormatter:
    def __init__(self, config):
        self.renaming_mappings = config.transformation.renaming_mappings
        self.attributes_to_add = config.transformation.attributes_to_add

    def __rename_variables(self, datasets):
        variables_to_remove = []
        for ds_name, renaming_map in self.renaming_mappings.items():
            if ds_name not in datasets:
                print(f"WARNING: Dataset '{ds_name}' not found for renaming. Skipping...")
                continue

            ds = datasets[ds_name]
            for var in renaming_map.keys():
                if (var not in ds) and (var not in ds.coords) and (var not in ds.dims):
                    print(f"WARNING: Variable '{var}' not found in dataset for renaming. Skipping...")
                    variables_to_remove.append(var)

            for var in variables_to_remove:
                renaming_map.pop(var)

            datasets[ds_name] = ds.rename(renaming_map)

    def __add_attributes(self, datasets):
        for ds_name, variables_and_attrs in self.attributes_to_add.items():
            if ds_name not in datasets:
                print(f"WARNING: Dataset '{ds_name}' not found for adding attributes. Skipping...")
                continue

            for variable, attrs in variables_and_attrs.items():
                if variable in datasets[ds_name]:
                    for attr_name, attr in attrs.items():
                        datasets[ds_name][variable].attrs[attr_name] = attr

    def __format_time(self, datasets: dict):
        for var, ds in datasets.items():
            source_file = ds.attrs.get("source_files", [None])[0]

    def transform_data(self, datasets):
        self.__rename_variables(datasets)
        self.__add_attributes(datasets)
        # self.__format_time(datasets)

import os
from dataclasses import dataclass, asdict
from subprocess import call
from typing import Any, Final, Callable

import etcd3
from etcd3 import Etcd3Client
from dacite import from_dict

"""
    ETCDConfig -

"""

@dataclass
class ETCDModuleConfigs:
    """
        Description of ETCDModuleConfigs class:
        `dirname: str` - Name of the directory that will contain all configuration in etcd (default=os.getenv('ETCD_SERVICE_NAME'))
        `gen_keys: bool` - Generate key in the etcd if it not exists
        `override_sys_object: bool` - Override the environment variable 
        `watch_keys: bool` - Watch for changes made in the etcd and get notified by a callback

    """
    dirname: str = None
    gen_keys: bool = False
    override_sys_object: bool = False
    watch_keys: bool = False

@dataclass
class ETCDPropertyDefenition:
    """
        Description of ETCDPropertyDefenition class:
        `etcd_path: str` - In case you want a custom path to load the value from, set this value with the path in the etcd
        `default_value: str = None` - 
    """
    etcd_path: str
    default_value: str = None

@dataclass
class EtcdConfigurations:
    """
        This class holds all the "client custom configurations" of the etcd.

        `module_configs: ETCDModuleConfigs` - A set of options that can be configured the way the class operates 
        `environment_params: dict[str, ETCDPropertyDefenition | str]` - Environment variables that you want to retrive/watch from the etcd
    """
    module_configs: ETCDModuleConfigs
    environment_params: dict[str, ETCDPropertyDefenition | str]


@dataclass
class ETCDConnectionConfigurations:
    """
        This class holds all the variables the etcd client can collect (retrived from the function "as-is")
    """
    host: str = 'localhost'
    port: int = 2379, 
    ca_cert: Any | None = None 
    cert_key: Any | None = None 
    cert_cert: Any | None = None 
    timeout: Any | None = None 
    user: Any | None = None 
    password: Any | None = None 
    grpc_options: Any | None = None

class ETCDConfig:
    default_configs: EtcdConfigurations = EtcdConfigurations(
        env_params={},
        module_configs=ETCDModuleConfigs(dirname=str(os.getenv('ETCD_SERVICE_NAME')))
    )

    etcd: Etcd3Client
    proccessed_configs: EtcdConfigurations
    # _etcd_watcher: Watcher
    env_params: dict[str, Any]

    def __init__(
        self,
        connection_configurations: ETCDConnectionConfigurations, 
        user_defined_configs: EtcdConfigurations
    ) -> None:
        try:
            self.etcd = etcd3.client(**connection_configurations)
            self.proccessed_configs = self._override_default_configs(user_defined_configs)
            self.env_params = {}

            if self.proccessed_configs.module_configs:
                if not self.proccessed_configs.module_config.dirname:
                    raise Exception('ETCD_SERVICE_NAME not found in environment variables')
            if not self.proccessed_configs.env_params:
                raise Exception('Configurations does not conatins any properties')
        except Exception as e:
            print('Exception occurred in ETCDConfig constructor', e)

    def _override_default_configs(user_defined_configs: EtcdConfigurations) -> EtcdConfigurations:
        """
            Overrides the default configurations with those the user specified
            args:
                `user_defined_configs: EtcdConfigurations` - The configurations the user specified
        """
        default_configs_dict: dict[str, Any] = asdict(default_configs_dict)
        user_defined_dict: dict[str, Any] = asdict(user_defined_configs)

        merged_dict: dict[str, Any] = { **default_configs_dict, **user_defined_dict }
        return from_dict(data_class=EtcdConfigurations, data=merged_dict)

    def _override_sys_object(self, property_name: str, val_to_override: Any) -> None:
        """
            Override the system environment variable, with the one got from the argument
            args:
                property_name: str - The environment key to override
                val_to_override: any - The value to set inside the environment variable
        """
        os.environ[property_name] = val_to_override

    def _watch_for_changes(
        self, etcd_entry_name: str, property_name: str, 
        callback: Callable[[Any, str, str], None] = None
    ) -> None:
        """
            Watches for changes in the etcd about the given etcd entry,
            And run the callback function
        """
        events_iterator, cancel = self.etcd.watch(etcd_entry_name)
        # for event in events_iterator:
        #     event
        
    
    def _start_fetch(self) -> None:
        """
            Trying to fetch the wanted parameters from the etcd,
            In case it failes, it will do the fallback mentioned at the top of this file
        """
        module_configs: ETCDModuleConfigs = self.proccessed_configs.module_configs
        env_params: dict[str, ETCDPropertyDefenition | str] = self.proccessed_configs.environment_params
        for property_name in env_params.keys():
            generated_path: Final[str] = f'{module_configs.dirname}/{property_name}'
            etcd_entry_name: str = generated_path
            default_val: Any = env_params[property_name]

            property_defenition: ETCDPropertyDefenition = None
            if type(env_params[property_name]) is ETCDPropertyDefenition:
                property_defenition = env_params[property_name]
                etcd_entry_name = property_defenition.etcd_path
                default_val = property_defenition.default_value

            try:
                etcd_res, metadata = self.etcd.get(etcd_entry_name)
                if module_configs.override_sys_object:
                    self._override_sys_object(property_name, etcd_res or default_val)
                env_params[property_name] = etcd_res or default_val

                # TODO: Add watch_for_key_changes support
                # if module_configs.watch_keys:
                #     self._watch_for_changes(etcd_entry_name, property_name)
                
                if not etcd_res or module_configs.gen_keys: 
                    self.etcd.put(etcd_entry_name, os.getenv(property_name))

            except Exception as e:
                print('exception occured in _start_fetch()', e)
             
    
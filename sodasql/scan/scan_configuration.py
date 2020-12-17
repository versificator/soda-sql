#  Copyright 2020 Soda
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from sodasql.scan.column import Column
from sodasql.scan.metric import Metric
from sodasql.scan.parse_logs import ParseLogs
from sodasql.scan.scan_configuration_column import ScanConfigurationColumn


class ScanConfiguration:

    VALID_KEYS = ['table_name', 'metrics', 'columns', 'sample_size']

    def __init__(self, scan_dict: dict):
        self.parse_logs = ParseLogs()
        self.table_name = scan_dict.get('table_name')
        if not self.table_name:
            self.parse_logs.error('table_name is required')
        self.metrics = ScanConfigurationColumn.resolve_metrics(scan_dict.get('metrics', []))
        if not isinstance(self.metrics, list):
            self.parse_logs.error('metrics is not a list')
        else:
            self.parse_logs.warning_invalid_elements(
                self.metrics,
                Metric.METRIC_TYPES,
                'Invalid metrics value')
        self.columns = {}
        columns_dict = scan_dict.get('columns', {})
        for column_name in columns_dict:
            column_dict = columns_dict[column_name]
            column_name_lower = column_name.lower()
            self.columns[column_name_lower] = ScanConfigurationColumn(column_name, column_dict, self.parse_logs)
        self.sample_size = scan_dict.get('sample_size')
        self.parse_logs.warning_invalid_elements(
            scan_dict.keys(),
            ScanConfiguration.VALID_KEYS,
            'Invalid scan configuration')

    def is_missing_enabled(self, column):
        for metric in self.__get_metrics(column):
            if metric in [Metric.MISSING_COUNT, Metric.MISSING_PERCENTAGE, Metric.VALUES_COUNT, Metric.VALUES_PERCENTAGE]:
                return True
        return False

    def is_valid_enabled(self, column):
        for metric in self.__get_metrics(column):
            if metric in [Metric.INVALID_COUNT, Metric.INVALID_PERCENTAGE, Metric.VALID_COUNT, Metric.VALID_PERCENTAGE]:
                return True
        return False

    def is_min_length_enabled(self, column):
        return self.__is_metric_enabled(column, Metric.MIN_LENGTH)

    def __is_metric_enabled(self, column: Column, metric: str):
        return metric in self.__get_metrics(column)

    def __get_metrics(self, column: Column):
        metrics = self.metrics.copy()
        column_configuration = self.columns.get(column.name.lower())
        if column_configuration is not None and column_configuration.metrics is not None:
            metrics.extend(column_configuration.metrics)
        return metrics

    def get_missing_values(self, column):
        column_configuration = self.columns.get(column.name.lower())
        return column_configuration.missing_values if column_configuration else None

    def get_validity(self, column):
        column_configuration = self.columns.get(column.name.lower())
        return column_configuration.validity if column_configuration else None
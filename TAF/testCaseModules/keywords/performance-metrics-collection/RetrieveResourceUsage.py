"""
 @copyright Copyright (C) 2020 IOTech Ltd

 @license SPDX-License-Identifier: Apache-2.0

 @file RetrieveResourceUsage.py

 @description

"""

import os
import paramiko
import traceback
import data_utils
from TUC.data.SettingsInfo import SettingsInfo
import docker
from robot.api import logger


global services
services = ["edgex-core-data", "edgex-core-metadata", "edgex-core-command", "edgex-support-notifications", "edgex-device-virtual", "edgex-kuiper"]


class RetrieveResourceUsage(object):

    def __init__(self):
        self._result = ""

    def get_test_services(self):
        profile_constant = __import__("TAF.config.performance-metrics.configuration", fromlist=['configuration'])
        SettingsInfo().add_name('profile_constant', profile_constant)
        return services

    def retrieve_cpu_and_memory_usage(self, test_services):
        global resource_usage
        resource_usage = {}

        for k in test_services:
            resource_usage[k] = fetch_by_service(k)
        return resource_usage

    def retrieve_cpu_aggregation_value(self, resource_list):
        return get_all_service_cpu_usage_aggregation(resource_list)

    def retrieve_mem_aggregation_value(self, resource_list):
        return get_all_service_mem_usage_aggregation(resource_list)

    def cpu_usage_is_over_than_threshold_setting(self):
        compare_cpu_usage(resource_usage)

    def memory_usage_is_over_than_threshold_setting(self):
        compare_mem_usage(resource_usage)

    def show_the_summary_table(self, results):
        show_the_summary_table_in_html(results)

    def show_the_cpu_aggregation_table(self, results):
        global cpu_usage
        cpu_usage = results
        show_the_cpu_aggregation_table_in_html(cpu_usage)

    def show_the_mem_aggregation_table(self, results):
        global mem_usage
        mem_usage = results
        show_the_mem_aggregation_table_in_html(mem_usage)


def get_Cpu_Mem_Usage(server, auth, serviceName, command_type):
    user = auth.split("/")[0]
    pswd = auth.split("/")[1]
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_session = None
    server = server.rstrip('\n')
    try:
        ssh_client.connect(server, username=user, password=pswd)
        if command_type == "cpu":
            command = "top -b -n 1 | grep "+serviceName+" | awk '{print $6}'"
        if command_type == "memory":
            command = "echo '"+pswd+"' | sudo -S pmap -x $(pgrep "+serviceName+") | grep total | awk '{print $2}'"
        ssh_session = ssh_client.get_transport().open_session()
        ssh_session.exec_command(command)
        output = ssh_session.recv(1024).decode("utf-8")
        lines = output.split('\n')
        value = lines[0].strip()
        ssh_client.close()
        return(value)
    except Exception as e:
        print("An error occurred:", str(e))


def fetch_by_service(service):
    data_file = os.getenv("DATA_FILE")
    with open(data_file,'r') as file:
        ip = str(file.read())
    auth = os.getenv("AUTH")
    serviceName = service.split("-", 1)
    serviceName = serviceName[1]
    usage = {}
    cpuUsage = get_Cpu_Mem_Usage(ip, auth, serviceName, "cpu")
    memoryUsage = get_Cpu_Mem_Usage(ip, auth, serviceName, "memory")
    usage["cpuUsage"] = format(float(cpuUsage), '.2f')
    usage["memoryUsage"] = format(int(memoryUsage) / 1000000, '.2f')
    return usage


def compare_cpu_usage(service_resource_list):
    threshold_value = SettingsInfo().profile_constant.CPU_USAGE_THRESHOLD
    for i in services:
        logger.info("{} cpu: {}".format(i, service_resource_list[i]["cpuUsage"]))
        if float(service_resource_list[i]["cpuUsage"]) > threshold_value:
            raise Exception("{} CPU usage in over than {} %".format(service_resource_list[i], threshold_value))
            return False
    return True


def compare_mem_usage(service_resource_list):
    threshold_value = SettingsInfo().profile_constant.MEM_USAGE_THRESHOLD
    for i in services:
        logger.info("{} memory: {}".format(i, service_resource_list[i]["memoryUsage"]))
        if float(service_resource_list[i]["memoryUsage"]) > threshold_value:
            raise Exception("{} memory usage in over than {} MB".format(service_resource_list[i], threshold_value))
            return False
    return True


def get_all_service_cpu_usage_aggregation(resource_list):
    all_services_cpu_usage = []
    for service in services:
        cpu_aggregation = get_service_cpu_aggregation_value(service, resource_list)
        agg_value = {
            "name": service,
            "max": cpu_aggregation["max"],
            "min": cpu_aggregation["min"],
            "avg": cpu_aggregation["avg"]
        }
        all_services_cpu_usage.append(agg_value)
    return all_services_cpu_usage


def get_all_service_mem_usage_aggregation(resource_list):
    all_services_mem_usage = []
    for service in services:
        mem_aggregation = get_service_mem_aggregation_value(service, resource_list)
        agg_value = {
            "name": service,
            "max": mem_aggregation["max"],
            "min": mem_aggregation["min"],
            "avg": mem_aggregation["avg"]
        }
        all_services_mem_usage.append(agg_value)
    return all_services_mem_usage


def get_service_cpu_aggregation_value(service, resource_list):
    service_cpu_usage = []
    for resource in resource_list:
        if resource.get(service) is None:
            raise Exception("Service {} is not existed.".format(service))

        cpu_usage = float(resource[service]["cpuUsage"])
        service_cpu_usage.append(cpu_usage)

    return data_utils.calculate_avg_max_min_from_list(service_cpu_usage)


def get_service_mem_aggregation_value(service, resource_list):
    service_mem_usage = []
    for resource in resource_list:
        if resource.get(service) is None:
            raise Exception("Service {} is not existed.".format(service))

        mem_usage = float(resource[service]["memoryUsage"])
        service_mem_usage.append(mem_usage)

    return data_utils.calculate_avg_max_min_from_list(service_mem_usage)


def calculate_memory_usage(d):
    memory_usage = 0
    try:
        memory_usage = d["memory_stats"]["usage"] - d["memory_stats"]["stats"]["cache"]
    except:
        logger.error("fail to calculate memory usage")
        logger.error(traceback.format_exc())
        return memory_usage

    return memory_usage


# https://github.com/docker/cli/blob/master/cli/command/container/stats_helpers.go#L100
def calculateCPUPercent(d):
    percent = 0
    percent = calculateCPUPercentUnix(d)
    return percent


def calculateCPUPercentUnix(v):
    # logger.console(v)
    previousCPU = v["precpu_stats"]["cpu_usage"]["total_usage"]
    previousSystem = v["precpu_stats"]["system_cpu_usage"]

    cpuPercent = 0.0
    # calculate the change for the cpu usage of the container in between readings
    cpuDelta = float(v["cpu_stats"]["cpu_usage"]["total_usage"]) - float(previousCPU)
    # calculate the change for the entire system between readings
    systemDelta = float(v["cpu_stats"]["system_cpu_usage"]) - float(previousSystem)
    onlineCPUs = float(v["cpu_stats"]["online_cpus"])

    if (onlineCPUs == 0.0):
        onlineCPUs = float(len(v["cpu_stats"]["cpu_usage"]["percpu_usage"]))

    if ((systemDelta > 0.0) and (cpuDelta > 0.0)):
        cpuPercent = (cpuDelta / systemDelta) * onlineCPUs * 100.0

    return cpuPercent


def show_the_summary_table_in_html(results):
    for res in results:
        html = """ 
        <h3 style="margin:0px">Full resource usage result:</h3>
        <table style="border: 1px solid black;white-space: initial;"> 
            <tr style="border: 1px solid black;">
                <th style="border: 1px solid black;">
                    Micro service			 	 
                </th>
                <th style="border: 1px solid black;">
                    Memory Usage
                </th>
                <th style="border: 1px solid black;">
                    CPU Usage
                </th>
            </tr>
        """

        for k in res:
            html = html + """ 
            <tr style="border: 1px solid black;">
                <td style="border: 1px solid black;">
                    {}			 	 
                </td>
                <td style="border: 1px solid black;">
                    {} MB
                </td>
                <td style="border: 1px solid black;">
                    {} %
                </td>
            </tr>
        """.format(
                k, res[k]["memoryUsage"], res[k]["cpuUsage"]
            )

        html = html + "</table>"
        logger.info(html, html=True)


def show_the_cpu_aggregation_table_in_html(results):
    html = """ 
    <h3 style="margin:0px">CPU usage aggregation:</h3>
    <h4 style="margin:0px;color:blue">Retrieve Resource Times: {} / Retrieve Resource Interval: {} seconds / Threshold: {}%</h4>
    <table style="border: 1px solid black;white-space: initial;"> 
        <tr style="border: 1px solid black;">
            <th style="border: 1px solid black;">
                Micro service			 	 
            </th>
            <th style="border: 1px solid black;">
                Maximum
            </th>
            <th style="border: 1px solid black;">
                Minimum
            </th>
            <th style="border: 1px solid black;">
                Average
            </th>
        </tr>
    """.format(SettingsInfo().profile_constant.GET_CPU_MEM_LOOP_TIMES,
               SettingsInfo().profile_constant.GET_CPU_MEM_INTERVAL,
               SettingsInfo().profile_constant.CPU_USAGE_THRESHOLD)

    for res in results:
        html = html + """ 
        <tr style="border: 1px solid black;">
            <td style="border: 1px solid black;">
                {}			 	 
            </td>
            <td style="border: 1px solid black;">
                {} %
            </td>
            <td style="border: 1px solid black;">
                {} %
            </td>
            <td style="border: 1px solid black;">
                {} %
            </td>
        </tr>
    """.format(
            res["name"], res["max"], res["min"], res["avg"]
        )

    html = html + "</table>"
    logger.info(html, html=True)
    return html


def show_the_mem_aggregation_table_in_html(results):
    html = """ 
        <h3 style="margin:0px">Memory usage aggregation:</h3>
        <h4 style="margin:0px;color:blue">Retrieve Resource Times: {} / Retrieve Resource Interval: {} seconds / Threshold: {}MB</h4>
        <table style="border: 1px solid black;white-space: initial;"> 
            <tr style="border: 1px solid black;">
                <th style="border: 1px solid black;">
                    Micro service			 	 
                </th>
                <th style="border: 1px solid black;">
                    Maximum
                </th>
                <th style="border: 1px solid black;">
                    Minimum
                </th>
                <th style="border: 1px solid black;">
                    Average
                </th>
            </tr>
        """.format(SettingsInfo().profile_constant.GET_CPU_MEM_LOOP_TIMES,
                   SettingsInfo().profile_constant.GET_CPU_MEM_INTERVAL,
                   SettingsInfo().profile_constant.MEM_USAGE_THRESHOLD)

    for res in results:
        html = html + """ 
            <tr style="border: 1px solid black;">
                <td style="border: 1px solid black;">
                    {}			 	 
                </td>
                <td style="border: 1px solid black;">
                    {} MB
                </td>
                <td style="border: 1px solid black;">
                    {} MB
                </td>
                <td style="border: 1px solid black;">
                    {} MB
                </td>
            </tr>
        """.format(
            res["name"], res["max"], res["min"], res["avg"]
        )

    html = html + "</table>"
    logger.info(html, html=True)
    return html

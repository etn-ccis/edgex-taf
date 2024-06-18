# This file is for making modification in EdgeX-TAF tests

import sys
import fileinput
import re

service = sys.argv[1]
target = sys.argv[2]


def swap(f_path, search_str, new_str):
    with fileinput.FileInput(f_path, inplace=True) as file:
        for line in file:
            if line == search_str:
                print(new_str, end='\n')
            else:
                print(line, end='')


def global_variable(file_path):
    """
    will do below action
        1. find BASE_URL from global_variables.py file and
           give default value as ""
            - if BASE_URL variable is not available then it will stop execution
        2. find DEPLOY_TYPE from global_variables.py file and set it
           as a generic which will set value from environment
            - if DEPLOY_TYPE variable is not available then it will
              stop execution
    """
    with open(file_path, 'r') as file:
        content = file.read()
        assert "BASE_URL" in content, print("-----BASE_URL does not exist in global_variables.py-----")
        swap(file_path, "BASE_URL = \"localhost\"\n", "BASE_URL = \"\"")
        assert "DEPLOY_TYPE" in content, print("-----DEPLOY_TYPE does not exist in global_variables.py-----")
        swap(file_path,
             "DEPLOY_TYPE = \"docker\"\n",
             "DEPLOY_TYPE = os.getenv(\"DEPLOY_TYPE\")")


def change_auth_type(file_path):
    """
    will change auth type from "Authorization=Bearer" to "X-Auth-Token"
    in whole file as in manual mode we are using X-Auth-Token method
    """
    with open(file_path, 'r') as f:
        newlines = []
        for line in f.readlines():
            newlines.append(line.replace('Authorization=Bearer ${jwt_token}',
                                         'X-Auth-Token=${jwt_token}'))
    with open(file_path, 'w') as f:
        for line in newlines:
            f.write(line)


def add_data(file_path, find, new_line):
    """
    will do below action
        1. will put specific line (i.e. new_line) in file.
    """
    with open(file_path, "r") as in_file:
        buf = in_file.readlines()
    with open(file_path, "w") as out_file:
        for line in buf:
            if find in line:
                line = line + new_line
            out_file.write(line)


def change_port(old_port, new_port):
    """
    Will replace port in global_variables.py file
    """
    with open('TAF/config/global_variables.py', 'rt') as f:
        newlines = []
        for line in f.readlines():
            newlines.append(line.replace(old_port, new_port))
    with open('TAF/config/global_variables.py', 'w') as f:
        for line in newlines:
            f.write(line)


def replace(file_path, old_str, new_str):
    with open(file_path, 'rt') as f:
        newlines = []
        for line in f.readlines():
            newlines.append(line.replace(old_str, new_str))
    with open(file_path, 'w') as f:
        for line in newlines:
            f.write(line)


def replace_lines(filename, old_lines, new_lines):
    # This will match and replace multiple lines
    with open(filename, 'r') as file:
        data = file.read()
        for old, new in zip(old_lines, new_lines):
            data = re.sub(re.escape(old), new, data)

    with open(filename, 'w') as file:
        file.write(data)


def add_newlines(filename, target_line, new_lines):
    # This will add multiple newlines
    with open(filename, 'r') as file:
        data = file.read()
        pattern = re.compile(rf'({re.escape(target_line)}\n)((?:.*\n)*)')
        data = pattern.sub(rf'\1\2{new_lines}\n', data)

    with open(filename, 'w') as file:
        file.write(data)


def replace_Paragraph_in_file(file_Path, paragraph_to_match, new_paragraph):
    # This can we use to replace multiple lines at once
    with open(file_Path, 'r') as file:
        file_content = file.read()
    if paragraph_to_match in file_content:
        updated_content = file_content.replace(paragraph_to_match, new_paragraph)
        with open(file_Path, 'w')as file:
            file.write(updated_content)
    else:
        print("Pragraph not found")
        print("Paragraph to match:")
        print(paragraph_to_match)


def add_new_data_below_paragraph(file_path, paragraph_to_match, new_data):
    # This is use to match the multiple line to get accurracy and then will add the new lines after matched lines
    with open(file_path, 'r') as file:
        file_content = file.read()
    if paragraph_to_match in file_content:
        index = file_content.find(paragraph_to_match) + len(paragraph_to_match)
        updated_content = file_content[:index] + new_data + file_content[index:]
        with open(file_path, 'w')as file:
            file.write(updated_content)
    else:
        print("Pragraph not found in add lines")
        print("Paragraph to match:")
        print(paragraph_to_match)


def general_changes():
    """
    Note: This function will do below task
        1. will modify "BASE_URL", "DEPLOY_TYPE" and "PORT <core-metadata> "
        2. will change Auth type in common files
        3. set IP address of qemu to "BASE_URL"
    """
    global_variable("TAF/config/global_variables.py")
    change_auth_type("TAF/testCaseModules/keywords/common/commonKeywords.robot")
    change_auth_type("TAF/testCaseModules/keywords/core-metadata/coreMetadataAPI.robot")
    change_auth_type("TAF/testCaseModules/keywords/core-data/coreDataAPI.robot")
    change_auth_type("TAF/testCaseModules/keywords/support-scheduler/supportSchedulerAPI.robot")
    change_auth_type("TAF/testCaseModules/keywords/support-notifications/cleanupAPI.robot")
    change_auth_type("TAF/testCaseModules/keywords/support-notifications/notificationAPI.robot")
    change_auth_type("TAF/testCaseModules/keywords/support-notifications/subscriptionAPI.robot")
    change_auth_type("TAF/testCaseModules/keywords/support-notifications/transmissionAPI.robot")
    change_port("8443/core-metadata", "80/metadata")
    change_port("8443/core-command", "80/command")
    change_port("8443/core-data", "80/coredata")
    change_port("8443/support-notifications", "80/notification")
    change_port("8443/support-scheduler", "80/scheduler")
    change_auth_type("TAF/testCaseModules/keywords/core-command/coreCommandAPI.robot")

    replace("TAF/testCaseModules/keywords/setup/startup_checker.py",
            "\"Authorization\": \"Bearer {}\"",
            "\"X-Auth-Token= {}\"")

    replace_lines("TAF/testCaseModules/keywords/setup/edgex.py",
                  ["checker.check_services_startup([\"data\", \"metadata\", \"command\", \"support-notifications\", \"support-scheduler\",",
                   "\"device-virtual\""],
                  ["#checker.check_services_startup([\"data\", \"metadata\", \"command\", \"support-notifications\", \"support-scheduler\",",
                   "#\"device-virtual\""])
    add_data("TAF/testCaseModules/keywords/setup/startup_checker.py",
             "import subprocess", "import os" + "\n")
    add_data("TAF/testCaseModules/keywords/setup/startup_checker.py",
             "def check_service_startup(d, token):",
             "    SettingsInfo().constant.BASE_URL=open(os.getenv(\"DATA_FILE\"), \"r\").read()\n    SettingsInfo().constant.BASE_URL=SettingsInfo("
             ").constant.BASE_URL[:-1]" + "\n")
    add_data("TAF/testCaseModules/keywords/common/commonKeywords.robot",
             "Set suite variable  ${response}  ${resp.status_code}",
             "    Set suite variable  ${body}  ${resp.json()}\n")
    replace("TAF/testCaseModules/keywords/common/commonKeywords.robot",
            "${coreCommandUrl}    ${URI_SCHEME}://${BASE_URL}:${CORE_COMMAND_PORT}",
            "${coreCommandUrl}    http://${BASE_URL}:${CORE_COMMAND_PORT}")
    replace("TAF/testCaseModules/keywords/common/commonKeywords.robot",
            "${default_response_time_threshold}  1200",
            "${default_response_time_threshold}  4000")
    replace("TAF/testCaseModules/keywords/core-command/coreCommandAPI.robot",
            "${coreCommandUrl}    ${URI_SCHEME}://${BASE_URL}:${CORE_COMMAND_PORT}",
            "${coreCommandUrl}    http://${BASE_URL}:${CORE_COMMAND_PORT}")
    replace("TAF/testCaseModules/keywords/core-data/coreDataAPI.robot",
            "${coreDataUrl}  ${URI_SCHEME}://${BASE_URL}:${CORE_DATA_PORT}",
            "${coreDataUrl}  http://${BASE_URL}:${CORE_DATA_PORT}")
    replace("TAF/testCaseModules/keywords/core-metadata/coreMetadataAPI.robot",
            "${coreMetadataUrl}   ${URI_SCHEME}://${BASE_URL}:${CORE_METADATA_PORT}",
            "${coreMetadataUrl}   http://${BASE_URL}:${CORE_METADATA_PORT}")
    replace("TAF/testCaseModules/keywords/support-notifications/cleanupAPI.robot",
            "${supportNotificationsUrl}   ${URI_SCHEME}://${BASE_URL}:${SUPPORT_NOTIFICATIONS_PORT}",
            "${supportNotificationsUrl}   http://${BASE_URL}:${SUPPORT_NOTIFICATIONS_PORT}")
    replace("TAF/testCaseModules/keywords/support-notifications/notificationAPI.robot",
            "${supportNotificationsUrl}   ${URI_SCHEME}://${BASE_URL}:${SUPPORT_NOTIFICATIONS_PORT}",
            "${supportNotificationsUrl}   http://${BASE_URL}:${SUPPORT_NOTIFICATIONS_PORT}")
    replace("TAF/testCaseModules/keywords/support-notifications/subscriptionAPI.robot",
            "${supportNotificationsUrl}   ${URI_SCHEME}://${BASE_URL}:${SUPPORT_NOTIFICATIONS_PORT}",
            "${supportNotificationsUrl}   http://${BASE_URL}:${SUPPORT_NOTIFICATIONS_PORT}")
    replace("TAF/testCaseModules/keywords/support-notifications/transmissionAPI.robot",
            "${supportNotificationsUrl}   ${URI_SCHEME}://${BASE_URL}:${SUPPORT_NOTIFICATIONS_PORT}",
            "${supportNotificationsUrl}   http://${BASE_URL}:${SUPPORT_NOTIFICATIONS_PORT}")
    add_data("TAF/testCaseModules/keywords/support-notifications/subscriptionAPI.robot",
             "*** Keywords ***",
             "\nGenerate ${number} Subscriptions Sample With EMAIL Channel\n    ${subscription_list}  Create List\n    FOR  ${INDEX}  IN RANGE  0  ${"
             "number}\n        ${index}=  Get current milliseconds epoch time\n        ${data}=  Get File  ${"
             "WORK_DIR}/TAF/testData/support-notifications/subscription_data.json  encoding=UTF-8\n        ${subscription}=  Evaluate  json.loads('''${"
             "data}''')  json\n        ${channel}=  Load data file \"support-notifications/channels_data.json\" and get variable \"EMAIL\"\n        Set To "
             "Dictionary  ${subscription}  name=Subscription-${index}\n        Set To Dictionary  ${subscription}  channels=${channel}\n        Append To "
             "List  ${subscription_list}  ${subscription}\n    END\n    Generate Subscriptions  @{subscription_list}\n\n")
    replace("TAF/testCaseModules/keywords/support-scheduler/supportSchedulerAPI.robot",
            "${supportSchedulerUrl}  ${URI_SCHEME}://${BASE_URL}:${SUPPORT_SCHEDULER_PORT}",
            "${supportSchedulerUrl}  http://${BASE_URL}:${SUPPORT_SCHEDULER_PORT}")
    replace("TAF/testScenarios/functionalTest/V2-API/core-command/device/GET-Positive.robot",
            "Given Create 5 Devices For device-virtual",
            "#Given Create 5 Devices For device-virtual")

    add_data("TAF/testScenarios/functionalTest/V2-API/core-command/device/GET-Positive.robot",
             "CommandGET001 - Query all DeviceCoreCommands",
             "    Given Set Test Variable  ${profile_name}  Virtual-Sample-Profile\n    And Generate A Device Profile Sample  ${profile_name}\n    And Create "
             "device profile ${deviceProfile}\n    And Create 5 Devices For device-virtual\n")
    add_data("TAF/testScenarios/functionalTest/V2-API/core-command/device/GET-Positive.robot",
             "CommandGET002 - Query all DeviceCoreCommands by offset",
             "    Given Set Test Variable  ${profile_name}  Virtual-Sample-Profile\n    And Generate A Device Profile Sample  ${profile_name}\n    And Create "
             "device profile ${deviceProfile}\n    And Create 5 Devices For device-virtual\n")
    add_data("TAF/testScenarios/functionalTest/V2-API/core-command/device/GET-Positive.robot",
             "CommandGET003 - Query all DeviceCoreCommands by limit",
             "    Given Set Test Variable  ${profile_name}  Virtual-Sample-Profile\n    And Generate A Device Profile Sample  ${profile_name}\n    And Create "
             "device profile ${deviceProfile}\n    And Create 5 Devices For device-virtual\n")
    replace("TAF/testScenarios/functionalTest/V2-API/core-command/device/GET-Positive.robot",
            "Given Create Device For device-virtual With Name ${device_name}",
            "#Given Create Device For device-virtual With Name ${device_name}")

    add_data("TAF/testScenarios/functionalTest/V2-API/core-command/device/GET-Positive.robot",
             "${device_name}  Set Variable  Random-Integer-Device",
             "    Given Set Test Variable  ${profile_name}  Virtual-Sample-Profile\n    And Generate A Device Profile Sample  ${profile_name}\n    And Create "
             "device profile ${deviceProfile}\n    And Create Device For device-virtual With Name ${device_name}\n")

    add_data("TAF/testScenarios/functionalTest/V2-API/core-command/device/GET-Positive.robot",
             "${device_name}  Set Variable  Random-Binary-Device",
             "    ${source_name}  Set Variable  EngineSpeed\n    Given Set Test Variable  ${profile_name}  Virtual-Sample-Profile\n    And Generate A Device "
             "Profile Sample  ${profile_name}\n    And Create device profile ${deviceProfile}\n    And Create Device For device-virtual With Name ${"
             "device_name}\n")
    add_data("TAF/testScenarios/functionalTest/V2-API/core-command/device/GET-Positive.robot",
             "${device_name}  Set Variable  Random-Boolean-Device",
             "    Given Set Test Variable  ${profile_name}  Virtual-Sample-Profile\n    And Generate A Device Profile Sample  ${profile_name}\n    And Create "
             "device profile ${deviceProfile}\n    And Create Device For device-virtual With Name ${device_name}\n    When Get Device ${device_name} Read "
             "Command PropellerSpeed With ds-returnevent:no\n")

    add_data("TAF/testScenarios/functionalTest/V2-API/core-command/device/GET-Positive.robot",
             "CommandGET007 - Get specified device read command when ds-pushevent is yes",
             "    [Tags]    skipped\n    #This is failing due to issue in core-data\n")

    add_data("TAF/testScenarios/functionalTest/V2-API/core-command/device/GET-Positive.robot",
             "${device_name}  Set Variable  Random-Float-Device",
             "    Given Set Test Variable  ${profile_name}  Virtual-Sample-Profile\n    And Generate A Device Profile Sample  ${profile_name}\n    And Create "
             "device profile ${deviceProfile}\n    And Create Device For device-virtual With Name ${device_name}\n    When Get Device ${device_name} Read "
             "Command PropellerSpeed With ds-pushevent:yes\n")
    replace("TAF/testScenarios/functionalTest/V2-API/core-command/device/GET-Positive.robot",
            "When Get Device ${device_name} Read Command Virtual_GenerateDeviceValue_Boolean_R With ds-returnevent=no",
            "#When Get Device ${device_name} Read Command Virtual_GenerateDeviceValue_Boolean_R With ds-returnevent=no")

    replace("TAF/testScenarios/functionalTest/V2-API/core-command/device/GET-Positive.robot",
            "${source_name}  Set Variable  Virtual_GenerateDeviceValue_Binary_R",
            "#${source_name}  Set Variable  Virtual_GenerateDeviceValue_Binary_R")

    replace("TAF/testScenarios/functionalTest/V2-API/core-command/device/GET-Positive.robot",
            "When Get Device ${device_name} Read Command Virtual_GenerateDeviceValue_Boolean_R With ds-returnevent=no",
            "#When Get Device ${device_name} Read Command Virtual_GenerateDeviceValue_Boolean_R With ds-returnevent=no")
    replace("TAF/testScenarios/functionalTest/V2-API/core-command/device/GET-Positive.robot",
            "When Get Device ${device_name} Read Command Virtual_GenerateDeviceValue_FLOAT32_R With ds-pushevent=yes",
            "#When Get Device ${device_name} Read Command Virtual_GenerateDeviceValue_FLOAT32_R With ds-pushevent=yes")

    replace("TAF/testScenarios/functionalTest/V2-API/core-command/device/GET-Negative.robot",
            "When Run Keyword And Expect Error  *  Query All DeviceCoreCommands With offset=8",
            "When Run Keyword And Expect Error  *  Query All DeviceCoreCommands With offset=25")

    add_data("TAF/testScenarios/functionalTest/V2-API/core-command/device/GET-Negative.robot",
             "ErrCommandGET011 - Get unavailable HTTP device read command",
             "    [Tags]  skipped\n    #This should be skip as device-onvif-camera not available for us with advantech\n")

    replace("TAF/testScenarios/functionalTest/V2-API/core-command/device/SET.robot",
            "[Tags]  SmokeTest",
            "    [Tags]    skipped\n    #skipping following line until discussion with developer\n    #[Tags]   SmokeTest")

    add_data("TAF/testScenarios/functionalTest/V2-API/core-command/device/SET.robot",
             "${device_name}  Set Variable  Random-Binary-Device",
             "     Given Set Test Variable  ${profile_name}  Virtual-Sample-Profile\n    And Generate A Device Profile Sample  ${profile_name}\n    And Create "
             "device profile ${deviceProfile}\n    And Create Device For device-virtual With Name ${device_name}\n")

    add_data("TAF/testScenarios/functionalTest/V2-API/core-command/device/SET.robot",
             "${device_name}  Set Variable  Random-Float-Device",
             "     Given Set Test Variable  ${profile_name}  Virtual-Sample-Profile\n    And Generate A Device Profile Sample  ${profile_name}\n    And Create "
             "device profile ${deviceProfile}\n    And Create Device For device-virtual With Name ${device_name}\n")

    replace("TAF/testScenarios/functionalTest/V2-API/core-command/device/SET.robot",
            "Given Create Device For device-virtual With Name ${device_name}",
            "#Given Create Device For device-virtual With Name ${device_name}")

    add_data("TAF/testScenarios/functionalTest/V2-API/core-data/event/GET-negative.robot",
             "ErrEventGET006 - Query event fails when persistData is false",
             "    [Tags]  skipped\n    #should be skip as we do not support Consul\n")

    add_data("TAF/testScenarios/functionalTest/V2-API/core-data/event/GET-positive.robot",
             "EventGET002 - Query all events by limit = -1 and MaxResultCount= 5",
             "    [Tags]  skipped\n    #should be skip as we do not support Consul\n")

    add_data("TAF/testScenarios/functionalTest/V2-API/core-metadata/deviceprofile/DELETE-DeviceCommand.robot",
             "ErrProfileCommandDELETE004 - Delete deviceCommand when StrictDeviceProfileChanges config is enabled",
             "    [Tags]  skipped\n    #Skipping this as we do not support Consul\n")

    add_data("TAF/testScenarios/functionalTest/V2-API/core-metadata/deviceprofile/DELETE-Negative-DeviceCommand.robot",
             "ErrProfileCommandDELETE004 - Delete deviceCommand when StrictDeviceProfileChanges config is enabled",
             "    [Tags]  skipped\n    #Skipping this as we do not support Consul")

    add_data("TAF/testScenarios/functionalTest/V2-API/core-metadata/deviceprofile/DELETE-DeviceResource.robot",
             "ErrProfileResourceDELETE005 - Delete deviceResource when StrictDeviceProfileChanges config is enabled",
             "    [Tags]  skipped\n    #Skipping this as we do not support Consul")

    add_data("TAF/testScenarios/functionalTest/V2-API/core-metadata/deviceprofile/DELETE-Negative.robot",
             "ErrProfileDELETE004 - Delete device profile by name when StrictDeviceProfileDeletes is true",
             "    [Tags]  skipped\n    #Skipping this as we do not support Consul")

    replace_Paragraph_in_file("TAF/testScenarios/functionalTest/V2-API/core-metadata/deviceprofile/GET-Positive.robot",
                              """ProfileGET002 - Query all device profiles by offset
    Given Generate Multiple Device Profiles Sample""",
                              """ProfileGET002 - Query all device profiles by offset
    #Given Generate Multiple Device Profiles Sample""")

    add_data("TAF/testScenarios/functionalTest/V2-API/core-metadata/deviceprofile/GET-Positive.robot",
             "ProfileGET002 - Query all device profiles by offset",
             "    Given Set Test Variable  ${profile_name}  Test-Profile-1\n    And Generate A Device Profile Sample  ${profile_name}\n")

    replace_Paragraph_in_file("TAF/testScenarios/functionalTest/V2-API/core-metadata/deviceprofile/GET-Positive.robot",
                              """    And totalCount Is Greater Than Zero And ${content}[profiles] Count Should Match totalCount-offset
    And Should Return Content-Type "application/json"
    And Response Time Should Be Less Than "${default_response_time_threshold}"ms
    [Teardown]  Delete Multiple Device Profiles By Names  Test-Profile-1  Test-Profile-2  Test-Profile-3""", """    And totalCount Is Greater Than Zero And ${content}[profiles] Count Should Match totalCount-offset
    And Should Return Content-Type "application/json"
    And Response Time Should Be Less Than "${default_response_time_threshold}"ms
    [Teardown]  Delete Multiple Device Profiles By Names  Test-Profile-1""")

    replace_Paragraph_in_file("TAF/testScenarios/functionalTest/V2-API/core-metadata/deviceprofile/GET-Positive.robot",
                              """ProfileGET001 - Query all device profiles
    [Tags]  SmokeTest
    Given Generate Multiple Device Profiles Sample
    And Create Device Profile ${deviceProfile}
    When Query All Device Profiles""",
                              """ProfileGET001 - Query all device profiles
    [Tags]  SmokeTest
    Given Generate Multiple Device Profiles Sample
    And Create Device Profile ${deviceProfile}
    When Query All Device Profiles With limit=50""")

    add_data("TAF/testScenarios/functionalTest/V2-API/core-metadata/deviceprofile/POST-Negative-Deviceresource.robot",
             "ErrProfileResourcePOST009 - Add deviceResource with invalid units value",
             "    [Tags]  skipped\n    #Skipping this as we do not support consul\n")

    add_data("TAF/testScenarios/functionalTest/V2-API/core-metadata/deviceprofile/POST-Negative-Uploadfile.robot",
             "ErrProfilePOSTUpload009 - Create device profile by upload file with invalid units property",
             "    [Tags]  skipped\n    #Skipping this as we do not support consul\n")

    add_data("TAF/testScenarios/functionalTest/V2-API/core-metadata/deviceprofile/POST-Negative.robot",
             "ErrProfilePOST009 - Create device profile with invalid units value",
             "    [Tags]  skipped\n    #Skipping this as we do not support consul\n")

    add_data("TAF/testScenarios/functionalTest/V2-API/core-metadata/deviceprofile/POST-Positive-Deviceresource.robot",
             "ProfileResourcePOST003 - Add multiple Resources on device profile with valid units property",
             "    [Tags]  skipped\n    #Skipping this as we do not support consul\n")

    add_data("TAF/testScenarios/functionalTest/V2-API/core-metadata/deviceprofile/POST-Positive.robot",
             "ProfilePOST005 - Create device profile with json body and contains valid unit value",
             "    [Tags]  skipped\n    #Skipping this as we do not support consul\n")

    add_data("TAF/testScenarios/functionalTest/V2-API/core-metadata/deviceprofile/POST-Positive.robot",
             "ProfilePOST006 - Create device profile by upload file and the update file contains valid unit value",
             "    [Tags]  skipped\n    #Skipping this as we do not support consul\n")

    add_data("TAF/testScenarios/functionalTest/V2-API/core-metadata/deviceprofile/PUT-Negative-UploadFile.robot",
             "ErrProfilePUTUpload008 - Update device profile by upload file when StrictDeviceProfileChanges is true",
             "    [Tags]  skipped\n    #Skipping this as we do not support consul\n")

    add_data("TAF/testScenarios/functionalTest/V2-API/core-metadata/deviceprofile/PUT-Negative-UploadFile.robot",
             "ErrProfilePUTUpload009 - Update device profile by upload file and the update file contains invalid unit value",
             "    [Tags]  skipped\n    #Skipping this as we do not support consul\n")

    add_data("TAF/testScenarios/functionalTest/V2-API/core-metadata/deviceprofile/PUT-Negative.robot",
             "ErrProfilePUT009 - Update device profile with invalid units value",
             "    [Tags]  skipped\n    #Skipping this as we do not support consul\n")

    add_data("TAF/testScenarios/functionalTest/V2-API/core-metadata/deviceprofile/PUT-Negative.robot",
             "ErrProfilePUT008 - Update device profile when StrictDeviceProfileChanges is true",
             "    [Tags]  skipped\n    #Skipping this as we do not support consul\n")

    add_data("TAF/testScenarios/functionalTest/V2-API/core-metadata/deviceprofile/PUT-Positive.robot",
             "ProfilePUT005 - Update device profiles by upload file and the update file contains valid unit value",
             "    [Tags]  skipped\n    #Skipping this as we do not support consul\n")

    add_data("TAF/testScenarios/functionalTest/V2-API/core-metadata/deviceprofile/PUT-Positive.robot",
             "ProfilePUT004 - Update a device profile with valid unit value",
             "    [Tags]  skipped\n    #Skipping this as we do not support consul\n")

    add_data("TAF/testScenarios/functionalTest/V2-API/core-metadata/info/GET.robot",
             "InfoGET005 - Query UoM",
             "    [Tags]  skipped\n    #Check with developer as it is not returning uom it is getting as {} this is bug\n")

    replace_Paragraph_in_file("TAF/testScenarios/functionalTest/V2-API/core-metadata/provisionwatcher/GET-Positive.robot",
                              "ProWatcherGET001 - Query all provision watcher\n    Given Create Multiple Profiles/Services And Generate Multiple Provision "
                              "Watchers Sample\n    And Create Provision Watcher ${provisionwatcher}\n    When Query All Provision Watchers\n    Then Should "
                              "Return Status Code \"200\" And provisionWatchers\n    And totalCount Should be 4  # device-onvif-camera will auto create a "
                              "provision watcher\n    And Should Be True  len(${content}[provisionWatchers]) == 4",
                              "ProWatcherGET001 - Query all provision watcher\n    Given Create Multiple Profiles/Services And Generate Multiple Provision "
                              "Watchers Sample\n    And Create Provision Watcher ${provisionwatcher}\n    When Query All Provision Watchers\n    Then Should "
                              "Return Status Code \"200\" And provisionWatchers\n    And totalCount Should be 3  # device-onvif-camera will auto create a "
                              "provision watcher\n    And Should Be True  len(${content}[provisionWatchers]) == 3")

    replace_Paragraph_in_file("TAF/testScenarios/functionalTest/V2-API/core-metadata/provisionwatcher/GET-Positive.robot",
                              """ProWatcherGET002 - Query all provision watcher with offset
    Given Create Multiple Profiles/Services And Generate Multiple Provision Watchers Sample
    And Create Provision Watcher ${provisionwatcher}
    When Query All Provision Watchers With offset=1
    Then Should Return Status Code "200" And provisionWatchers
    And Should Return Content-Type "application/json"
    And totalCount Should be 4  # device-onvif-camera will auto create a provision watcher
    And Should Be True  len(${content}[provisionWatchers]) == 3""",
                              """ProWatcherGET002 - Query all provision watcher with offset
    Given Create Multiple Profiles/Services And Generate Multiple Provision Watchers Sample
    And Create Provision Watcher ${provisionwatcher}
    When Query All Provision Watchers With offset=1
    Then Should Return Status Code "200" And provisionWatchers
    And Should Return Content-Type "application/json"
    And totalCount Should be 3  # device-onvif-camera will auto create a provision watcher
    And Should Be True  len(${content}[provisionWatchers]) == 2""")

    replace_Paragraph_in_file("TAF/testScenarios/functionalTest/V2-API/core-metadata/provisionwatcher/GET-Positive.robot",
                              """ProWatcherGET003 - Query all provision watcher with limit
    Given Create Multiple Profiles/Services And Generate Multiple Provision Watchers Sample
    And Create Provision Watcher ${provisionwatcher}
    When Query All Provision Watchers With limit=2
    Then Should Return Status Code "200" And provisionWatchers
    And totalCount Should be 4  # device-onvif-camera will auto create a provision watcher""",
                              """ProWatcherGET003 - Query all provision watcher with limit
    Given Create Multiple Profiles/Services And Generate Multiple Provision Watchers Sample
    And Create Provision Watcher ${provisionwatcher}
    When Query All Provision Watchers With limit=2
    Then Should Return Status Code "200" And provisionWatchers
    And totalCount Should be 3  # device-onvif-camera will auto create a provision watcher""")

    replace("TAF/testScenarios/functionalTest/V2-API/support-notifications/notification/GET-Positive-II.robot",
            "${start}=  Get current milliseconds epoch time",
            "${start_current}=  Get current milliseconds epoch time\n    ${start}=    evaluate   int(${start_current}-10500)")

    replace("TAF/testScenarios/functionalTest/V2-API/support-notifications/notification/GET-Positive-II.robot",
            "${end}=  Get current milliseconds epoch time",
            "${end_current}=  Get current milliseconds epoch time\n    ${end}=    evaluate   int(${end_current}+10500)")

    replace("TAF/testScenarios/functionalTest/V2-API/support-notifications/notification/GET-Positive.robot",
            "ESCALATED",
            "PROCESSED")

    replace_Paragraph_in_file("TAF/testScenarios/functionalTest/V2-API/support-notifications/notification/GET-Positive.robot",
                              """    When Query All Notifications By Status  PROCESSED
    Then Should Return Status Code "200" And notifications
    And Should Return Content-Type "application/json"
    And Response Time Should Be Less Than "${default_response_time_threshold}"ms
    And Should Be True  len(${content}[notifications]) == 1
    And totalCount Should be 1""", """    When Query All Notifications By Status  PROCESSED
    Then Should Return Status Code "200" And notifications
    And Should Return Content-Type "application/json"
    And Response Time Should Be Less Than "${default_response_time_threshold}"ms
    And Should Be True  len(${content}[notifications]) >= 1
    And totalCount Should be 3""")

    replace("TAF/testScenarios/functionalTest/V2-API/support-notifications/transmission/GET-Positive-II.robot",
            "${end}=  Get current milliseconds epoch time",
            "${end_current}=  Get current milliseconds epoch time\n    ${end}=    evaluate   int(${end_current}+10500)")

    replace("TAF/testScenarios/functionalTest/V2-API/support-notifications/transmission/GET-Positive-II.robot",
            "${start}=  Get current milliseconds epoch time",
            "${start_current}=  Get current milliseconds epoch time\n    ${start}=    evaluate   int(${start_current}-10500)")

    add_data("TAF/testScenarios/functionalTest/V2-API/support-notifications/transmission/GET-Positive-II.robot",
             "TransmissionGET011 - Query transmissions By Id",
             "    [Tags]  skipped\n    #Skipping this as we do not support consul\n")

    replace("TAF/testScenarios/functionalTest/V2-API/support-notifications/transmission/GET-Positive-II.robot",
            "Generate A Subscription Sample With REST Channel",
            "Generate A Subscription Sample With EMAIL Channel")

    replace("TAF/testScenarios/functionalTest/V2-API/support-notifications/transmission/GET-Positive-II.robot",
            "Set To Dictionary  ${subscription}[0][subscription]  resendLimit=${resendLimit}",
            "#Set To Dictionary  ${subscription}[0][subscription]  resendLimit=${resendLimit}")

    replace("TAF/testScenarios/functionalTest/V2-API/support-notifications/transmission/GET-Positive.robot",
            "Generate 2 Subscriptions Sample With REST Channel",
            "Generate 2 Subscriptions Sample With EMAIL Channel")

    replace("TAF/testScenarios/functionalTest/V2-API/support-notifications/transmission/GET-Positive.robot",
            "sleep  1s  # Waiting for transmission status ESCALATED",
            "sleep  4s  # Waiting for transmission status ESCALATED")
    replace("TAF/testScenarios/functionalTest/V2-API/support-notifications/transmission/GET-Positive.robot",
            "sleep  2s  # Waiting for transmission status ESCALATED",
            "sleep  3s  # Waiting for transmission status ESCALATED")

    replace_lines("TAF/testScenarios/functionalTest/V2-API/support-notifications/transmission/GET-Positive.robot",
                  ["Set To Dictionary  ${subscription}[0][subscription]  resendLimit=${resendLimit}",
                   "Set To Dictionary  ${subscription}[0][subscription]  resendInterval=1s",
                   "Set To Dictionary  ${subscription}[0][subscription][channels][0]  host=${DOCKER_HOST_IP}",
                   "Set To Dictionary  ${subscription}[1][subscription]  resendLimit=${resendLimit}"],
                  ["#Set To Dictionary  ${subscription}[0][subscription]  resendLimit=${resendLimit}",
                   "#Set To Dictionary  ${subscription}[0][subscription]  resendInterval=1s",
                   "#Set To Dictionary  ${subscription}[0][subscription][channels][0]  host=${DOCKER_HOST_IP}",
                   "#Set To Dictionary  ${subscription}[1][subscription]  resendLimit=${resendLimit}"])
    add_new_data_below_paragraph("TAF/testScenarios/functionalTest/V2-API/support-notifications/transmission/GET-Positive-II.robot",
                                 """TransmissionGET012 - Query transmissions by subscription
    Given Create Subscriptions And Notifications""",
                                 """\n    sleep  10s""")

    add_data("TAF/testScenarios/functionalTest/V2-API/support-scheduler/intervalaction/POST-Positive.robot",
             "IntervalactionPOST002 - Create pre-created intervalaction with pre-created interval",
             "    [Tags]  skipped\n    #Skipping this as we do not support consul\n")


def main():
    general_changes()
    if service == "core-metadata":
        # This is core-metadata service specific changes
        # add a variable in GET-Positive.robot file which contain response device length
        add_data("TAF/testScenarios/functionalTest/V2-API/core-metadata/device/GET-Positive.robot",
                 "When Query All Devices\n",
                 "    ${length}=    Get Length    ${body}[devices]\n")
        # add a variable in GET-Positive.robot file which contain response object length with offset as 2
        add_data("TAF/testScenarios/functionalTest/V2-API/core-metadata/device/GET-Positive.robot",
                 "When Query All Devices With offset=2\n",
                 "    ${length}=    Get Length    ${body}[devices]\n")
        # Replacing device count 7 with velue of variable length in GET-Positive.robot file
        replace("TAF/testScenarios/functionalTest/V2-API/core-metadata/device/GET-Positive.robot",
                "== 7",
                "== ${length}")
        # Replacing device count 5 with velue of variable length with offset as 2 in GET-Positive.robot file
        replace("TAF/testScenarios/functionalTest/V2-API/core-metadata/device/GET-Positive.robot",
                "== 5",
                "== ${length}")
        # add a variable in GET-Positive.robot file which contain response device profile length
        add_data("TAF/testScenarios/functionalTest/V2-API/core-metadata/deviceprofile/GET-Positive.robot",
                 "When Query All Device Profiles\n",
                 "    ${length}=    Get Length    ${body}[profiles]\n")
        # add a variable in GET-Positive.robot file which contain response object length with offset as 2
        add_data("TAF/testScenarios/functionalTest/V2-API/core-metadata/deviceprofile/GET-Positive.robot",
                 "When Query All Device Profiles With offset=2\n",
                 "    ${length}=    Get Length    ${body}[profiles]\n")
        # Replacing device profile count 8 with velue of variable length in GET-Positive.robot file
        replace("TAF/testScenarios/functionalTest/V2-API/core-metadata/deviceprofile/GET-Positive.robot",
                "== 8",
                "== ${length}")
        # Replacing device profile count 5 with velue of variable length with offset as 2 in GET-Positive.robot file
        replace("TAF/testScenarios/functionalTest/V2-API/core-metadata/deviceprofile/GET-Positive.robot",
                "== 6",
                "== ${length}")
        # add a variable in GET-Positive.robot file which contain response device service length
        add_data("TAF/testScenarios/functionalTest/V2-API/core-metadata/deviceservice/GET-Positive.robot",
                 "When Query All Device Services\n",
                 "    ${length}=    Get Length    ${body}[services]\n")
        # add a variable in GET-Positive.robot file which contain response object length with offset as 2
        add_data("TAF/testScenarios/functionalTest/V2-API/core-metadata/deviceservice/GET-Positive.robot",
                 "When Query All Device Services With offset=2\n",
                 "    ${length}=    Get Length    ${body}[services]\n")
        # Replacing device service count 6 with velue of variable length in GET-Positive.robot file
        replace("TAF/testScenarios/functionalTest/V2-API/core-metadata/deviceservice/GET-Positive.robot",
                "== 6",
                "== ${length}")
        # Replacing device service count 5 with velue of variable length with offset as 2 in GET-Positive.robot file
        replace("TAF/testScenarios/functionalTest/V2-API/core-metadata/deviceservice/GET-Positive.robot",
                "== 4",
                "== ${length}")
    if service == "core-data":
        # Skipping this test as this test is taking count from docker image and it is not available in our image
        add_data("TAF/testScenarios/functionalTest/V2-API/core-data/event/DELETE-positive.robot",
                 "EventDELETE001 - Delete event by ID\n",
                 "    [Tags]    Skipped\n")
        # Skipping this test as this test is taking count from docker image and it is not available in our image
        add_data("TAF/testScenarios/functionalTest/V2-API/core-data/event/DELETE-positive.robot",
                 "EventDELETE002 - Delete events with specified device by device name\n",
                 "    [Tags]    Skipped\n")
        # Replacing count
        replace("TAF/testScenarios/functionalTest/V2-API/core-data/event/DELETE-positive.robot",
                "${count}  3",
                "${count}  0")
        # Replacing count
        replace("TAF/testScenarios/functionalTest/V2-API/core-data/event/DELETE-positive.robot",
                "${content}[Count]  6",
                "${content}[Count]  0")
        # Skipping this test as this test is taking count from docker image and it is not available in our image
        replace("TAF/testScenarios/functionalTest/V2-API/core-data/event/GET-positive.robot",
                "[Tags]  SmokeTest",
                "[Tags]  SmokeTest   Skipped")
        # Skipping this test as this test is taking count from docker image and it is not available in our image
        add_data("TAF/testScenarios/functionalTest/V2-API/core-data/event/GET-positive.robot",
                 "EventGET003 - Query all events with specified device by device name\n",
                 "    [Tags]    Skipped\n")
        # Skipping this test as this test is taking count from docker image and it is not available in our image
        add_data("TAF/testScenarios/functionalTest/V2-API/core-data/event/GET-positive.robot",
                 "EventGET004 - Query events by start/end time\n",
                 "    [Tags]    Skipped\n")
        # Replacing count
        replace("TAF/testScenarios/functionalTest/V2-API/core-data/event/GET-positive.robot",
                "${content}[Count]  6",
                "${content}[Count]  0")
        # Replacing count
        replace("TAF/testScenarios/functionalTest/V2-API/core-data/event/GET-positive.robot",
                "${content}[Count]  3",
                "${content}[Count]  0")
        # Replacing count
        replace("TAF/testScenarios/functionalTest/V2-API/core-data/event/GET-positive.robot",
                "${count}  6",
                "${count}  0")
        # Replacing count
        replace("TAF/testScenarios/functionalTest/V2-API/core-data/event/GET-positive.robot",
                "${count}  3",
                "${count}  0")
        # Replacing Expected response
        replace("TAF/testScenarios/functionalTest/V2-API/core-data/event/POST-negative.robot",
                "409",
                "201")
        # Skipping this test as this test is taking count from docker image and it is not available in our image
        add_data("TAF/testScenarios/functionalTest/V2-API/core-data/reading/GET-positive.robot",
                 "ReadingGET001 - Query all readings\n",
                 "    [Tags]    Skipped\n")
        # Skipping this test as this test is taking count from docker image and it is not available in our image
        add_data("TAF/testScenarios/functionalTest/V2-API/core-data/reading/GET-positive.robot",
                 "ReadingGET002 - Query all readings with offset\n",
                 "    [Tags]    Skipped\n")
        # Skipping this test as this test is taking count from docker image and it is not available in our image
        add_data("TAF/testScenarios/functionalTest/V2-API/core-data/reading/GET-positive.robot",
                 "ReadingGET003 - Query all readings with limit\n",
                 "    [Tags]    Skipped\n")
        # Skipping this test as this test is taking count from docker image and it is not available in our image
        add_data("TAF/testScenarios/functionalTest/V2-API/core-data/reading/GET-positive.robot",
                 "ReadingGET004 - Query reading by resoucreName\n",
                 "    [Tags]    Skipped\n")
        # Skipping this test as this test is taking count from docker image and it is not available in our image
        add_data("TAF/testScenarios/functionalTest/V2-API/core-data/reading/GET-positive.robot",
                 "ReadingGET005 - Query all readings with specified device by device name\n",
                 "    [Tags]    Skipped\n")
        # Skipping this test as this test is taking count from docker image and it is not available in our image
        add_data("TAF/testScenarios/functionalTest/V2-API/core-data/reading/GET-positive.robot",
                 "ReadingGET006 - Query readings by start/end time\n",
                 "    [Tags]    Skipped\n")
        # Replacing count
        replace("TAF/testScenarios/functionalTest/V2-API/core-data/reading/GET-positive.robot",
                "${content}[Count]  9",
                "${content}[Count]  0")
        # Replacing count
        replace("TAF/testScenarios/functionalTest/V2-API/core-data/reading/GET-positive.robot",
                "${content}[Count]  6",
                "${content}[Count]  0")
    if service == "core-command":
        # This is core-metadata service specific changes
        # Changing offset as 12 from 8
        replace("TAF/testScenarios/functionalTest/V2-API/core-command/device/GET-Negative.robot",
                "offset=8",
                "offset=12")
        # adding a tag Skipped as this test is depends on random service which is not available in build
        add_data("TAF/testScenarios/functionalTest/V2-API/core-command/device/GET-Negative.robot",
                 "Get specified device read command when device AdminState is locked\n",
                 "    [Tags]    Skipped\n")
        # adding a tag Skipped as this test is depends on random service which is not available in build
        add_data("TAF/testScenarios/functionalTest/V2-API/core-command/device/GET-Negative.robot",
                 "Get specified device read command when device OperatingState is down\n",
                 "    [Tags]    Skipped\n")
        # adding a tag Skipped as this test is depends on random service which is not available in build
        add_data("TAF/testScenarios/functionalTest/V2-API/core-command/device/GET-Positive.robot",
                 "Query DeviceCoreCommand by device name\n",
                 "    [Tags]    Skipped\n")
        # adding a tag Skipped as this test is depends on random service which is not available in build
        add_data("TAF/testScenarios/functionalTest/V2-API/core-command/device/GET-Positive.robot",
                 "Get specified device read command\n",
                 "    [Tags]    Skipped\n")
        # adding a tag Skipped as this test is depends on random service which is not available in build
        add_data("TAF/testScenarios/functionalTest/V2-API/core-command/device/GET-Positive.robot",
                 "Get specified device read command when ds-returnevent is no\n",
                 "    [Tags]    Skipped\n")
        # adding a tag Skipped as this test is depends on random service which is not available in build
        add_data("TAF/testScenarios/functionalTest/V2-API/core-command/device/GET-Positive.robot",
                 "Get specified device read command when ds-pushevent is yes\n",
                 "    [Tags]    Skipped\n")
        # adding a tag Skipped as this test is depends on random service which is not available in build
        replace("TAF/testScenarios/functionalTest/V2-API/core-command/device/SET.robot",
                "[Tags]  SmokeTest",
                "[Tags]  SmokeTest  Skipped")
        # adding a tag Skipped as this test is depends on random service which is not available in build
        add_data("TAF/testScenarios/functionalTest/V2-API/core-command/device/SET.robot",
                 "Set specified device write command when device is locked\n",
                 "    [Tags]    Skipped\n")
        # add a variable in GET-Positive.robot file which contain response device service length
        add_data("TAF/testScenarios/functionalTest/V2-API/core-command/device/GET-Positive.robot",
                 "When Query All DeviceCoreCommands\n",
                 "    ${length}=    Get Length    ${body}[deviceCoreCommands]\n")
        # Replacing devicecorecommands count 8 with velue of variable length in GET-Positive.robot file
        replace("TAF/testScenarios/functionalTest/V2-API/core-command/device/GET-Positive.robot",
                "== 8",
                "== ${length}")
        # add a variable in GET-Positive.robot file which contain response device service length
        add_data("TAF/testScenarios/functionalTest/V2-API/core-command/device/GET-Positive.robot",
                 "When Query All DeviceCoreCommands With offset=2\n",
                 "    ${length}=    Get Length    ${body}[deviceCoreCommands]\n")
        # Replacing devicecorecommands count 6 with velue of variable length in GET-Positive.robot file
        replace("TAF/testScenarios/functionalTest/V2-API/core-command/device/GET-Positive.robot",
                "== 6",
                "== ${length}")

    if service == "support-scheduler":
        # Modify condition for checking the length
        replace("TAF/testScenarios/functionalTest/V2-API/support-scheduler/interval/GET.robot",
                "== 4",
                ">= 4")
        # Modify condition for checking the length
        replace("TAF/testScenarios/functionalTest/V2-API/support-scheduler/interval/GET.robot",
                "== 3",
                ">= 3")
        # Modify condition for checking the length
        replace("TAF/testScenarios/functionalTest/V2-API/support-scheduler/interval/GET.robot",
                "== 22",
                ">= 22")
        # Skiped this test as this test depend on docker image
        add_data("TAF/testScenarios/functionalTest/V2-API/support-scheduler/intervalaction/GET.robot",
                 "IntervalactionGET006 - Query all Intervalactions by limit = -1 and MaxResultCount= 5\n",
                 "    [Tags]    Skipped\n")
    if service == "support-notifications":
        # Modified condition for checking current devices
        replace("TAF/testScenarios/functionalTest/V2-API/support-notifications/subscription/GET-Positive-II.robot",
                "== 2",
                ">= 2")
        # Modified condition for checking current devices
        replace("TAF/testScenarios/functionalTest/V2-API/support-notifications/subscription/GET-Positive-II.robot",
                "== 3",
                ">= 3")
        # Modified condition for checking current devices
        replace("TAF/testScenarios/functionalTest/V2-API/support-notifications/subscription/GET-Positive.robot",
                "== 3",
                ">= 3")
        # Modified condition for checking current devices
        replace("TAF/testScenarios/functionalTest/V2-API/support-notifications/subscription/GET-Positive.robot",
                "== 2",
                ">= 2")
        # Modified condition for checking current devices
        replace("TAF/testScenarios/functionalTest/V2-API/support-notifications/transmission/GET-Positive.robot",
                "== 4",
                ">= 4")
        # Modified condition for checking current devices
        replace("TAF/testScenarios/functionalTest/V2-API/support-notifications/transmission/GET-Positive.robot",
                "== 3",
                ">= 3")
        # Skiping this test as this test need to check on v2.3.0
        add_data("TAF/testScenarios/functionalTest/V2-API/support-notifications/cleanup/DELETE.robot",
                 "Cleanup001 - Cleanup\n",
                 "    [Tags]    Skipped\n")
        # Skiping this test as this test need to check on v2.3.0
        add_data("TAF/testScenarios/functionalTest/V2-API/support-notifications/cleanup/DELETE.robot",
                 "Cleanup002 - Cleanup by age\n",
                 "    [Tags]    Skipped\n")
        # Skiping this test as this test need to check on v2.3.0
        add_data("TAF/testScenarios/functionalTest/V2-API/support-notifications/notification/GET-Negative-II.robot",
                 "ErrNotificationGET015 - Query notifications by start/end time with invalid offset range\n",
                 "    [Tags]    Skipped\n")
        # Skiping this test as this test need to check on v2.3.0
        add_data("TAF/testScenarios/functionalTest/V2-API/support-notifications/notification/GET-Positive-II.robot",
                 "NotificationGET010 - Query notifications with time range\n",
                 "    [Tags]    Skipped\n")
        # Skiping this test as this test need to check on v2.3.0
        add_data("TAF/testScenarios/functionalTest/V2-API/support-notifications/notification/GET-Positive-II.robot",
                 "NotificationGET011 - Query notifications with time range by offset\n",
                 "    [Tags]    Skipped\n")
        # Skiping this test as this test need to check on v2.3.0
        add_data("TAF/testScenarios/functionalTest/V2-API/support-notifications/notification/GET-Positive-II.robot",
                 "NotificationGET012 - Query notifications with time range by limit\n",
                 "    [Tags]    Skipped\n")
        # Skiping this test as this test need to check on v2.3.0
        add_data("TAF/testScenarios/functionalTest/V2-API/support-notifications/notification/POST.robot",
                 "ErrNotificationPOST001 - Create notification with empty content\n",
                 "    [Tags]    Skipped\n")
        # Skiping this test as this test need to check on v2.3.0
        add_data("TAF/testScenarios/functionalTest/V2-API/support-notifications/notification/POST.robot",
                 "ErrNotificationPOST002 - Create notification with empty sender\n",
                 "    [Tags]    Skipped\n")
        # Skiping this test as this test need to check on v2.3.0
        add_data("TAF/testScenarios/functionalTest/V2-API/support-notifications/notification/POST.robot",
                 "ErrNotificationPOST003 - Create notification with invalid sender\n",
                 "    [Tags]    Skipped\n")
        # Skiping this test as this test need to check on v2.3.0
        add_data("TAF/testScenarios/functionalTest/V2-API/support-notifications/notification/POST.robot",
                 "ErrNotificationPOST004 - Create notification with empty severity\n",
                 "    [Tags]    Skipped\n")
        # Skiping this test as this test need to check on v2.3.0
        add_data("TAF/testScenarios/functionalTest/V2-API/support-notifications/notification/POST.robot",
                 "ErrNotificationPOST005 - Create notification with invalid severity\n",
                 "    [Tags]    Skipped\n")
        # Skiping this test as this test need to check on v2.3.0
        add_data("TAF/testScenarios/functionalTest/V2-API/support-notifications/notification/POST.robot",
                 "ErrNotificationPOST006 - Create notification with empty categories and labels\n",
                 "    [Tags]    Skipped\n")
        # Skiping this test as this test need to check on v2.3.0
        add_data("TAF/testScenarios/functionalTest/V2-API/support-notifications/notification/POST.robot",
                 "ErrNotificationPOST007 - Create notification with invalid status\n",
                 "    [Tags]    Skipped\n")
        # Skiping this test as this test need to check on v2.3.0
        add_data("TAF/testScenarios/functionalTest/V2-API/support-notifications/transmission/GET-Negative-II.robot",
                 "ErrTransmissionGET015 - Query transmissions by start/end time with invalid offset range\n",
                 "    [Tags]    Skipped\n")
        # Skiping this test as this test need to check on v2.3.0
        add_data("TAF/testScenarios/functionalTest/V2-API/support-notifications/transmission/GET-Negative.robot",
                 "ErrTransmissionGET001 - Query all transmissions with invalid offset range\n",
                 "    [Tags]    Skipped\n")
        # Skiping this test as this test need to check on v2.3.0
        add_data("TAF/testScenarios/functionalTest/V2-API/support-notifications/transmission/GET-Negative.robot",
                 "ErrTransmissionGET004 - Query transmissions by status with invalid offset range\n",
                 "    [Tags]    Skipped\n")
        # Skiping this test as this test need to check on v2.3.0
        add_data("TAF/testScenarios/functionalTest/V2-API/support-notifications/transmission/GET-Positive-II.robot",
                 "TransmissionGET008 - Query transmissions with time range\n",
                 "    [Tags]    Skipped\n")
        # Skiping this test as this test need to check on v2.3.0
        add_data("TAF/testScenarios/functionalTest/V2-API/support-notifications/transmission/GET-Positive-II.robot",
                 "TransmissionGET009 - Query transmissions with time range by offset\n",
                 "    [Tags]    Skipped\n")
        # Skiping this test as this test need to check on v2.3.0
        add_data("TAF/testScenarios/functionalTest/V2-API/support-notifications/transmission/GET-Positive-II.robot",
                 "TransmissionGET010 - Query transmissions with time range by limit\n",
                 "    [Tags]    Skipped\n")
        # Skiping this test as this test need to check on v2.3.0
        add_data("TAF/testScenarios/functionalTest/V2-API/support-notifications/transmission/GET-Positive.robot",
                 "TransmissionGET005 - Query transmissions with specified status\n",
                 "    [Tags]    Skipped\n")
        # Skiping this test as this test need to check on v2.3.0
        add_data("TAF/testScenarios/functionalTest/V2-API/support-notifications/transmission/GET-Positive.robot",
                 "TransmissionGET006 - Query transmissions with specified status by offset\n",
                 "    [Tags]    Skipped\n")
        # Skiping this test as this test need to check on v2.3.0
        add_data("TAF/testScenarios/functionalTest/V2-API/support-notifications/transmission/GET-Positive.robot",
                 "TransmissionGET007 - Query transmissions with specified status by limit\n",
                 "    [Tags]    Skipped\n")

    if service == "4_ping_response_time" or service == "performance-metrics-collection":
        # Added dependent library in test robot file
        add_data("TAF/testScenarios/performanceTest/performance-metrics-collection/4_ping_response_time/ping_response_time.robot",
                 "Resource        TAF/testCaseModules/keywords/common/commonKeywords.robot\n",
                 "Variables       TAF/config/performance-metrics/configuration.py\n")
        # Remove service ping as service is not available in swagger but was available in docker container
        replace("TAF/testScenarios/performanceTest/performance-metrics-collection/4_ping_response_time/ping_response_time.robot",
                "${SYS_MGMT_RES_LIST}=  Ping API for service  sys-mgmt-agent  ${SYS_MGMT_AGENT_PORT}",
                "# ${SYS_MGMT_RES_LIST}=  Ping API for service  sys-mgmt-agent  ${SYS_MGMT_AGENT_PORT}")
        # Remove service ping as service is not available in swagger but was available in docker container
        replace("TAF/testScenarios/performanceTest/performance-metrics-collection/4_ping_response_time/ping_response_time.robot",
                "Record response   edgex-sys-mgmt-agent",
                "# Record response   edgex-sys-mgmt-agent")
        # Remove service ping as service is not available in swagger but was available in docker container
        replace("TAF/testScenarios/performanceTest/performance-metrics-collection/4_ping_response_time/ping_response_time.robot",
                "${DEVICE_REST_RES_LIST}=  Ping API for service  device-rest  ${DEVICE_REST_PORT}",
                "# ${DEVICE_REST_RES_LIST}=  Ping API for service  device-rest  ${DEVICE_REST_PORT}")
        replace("TAF/testScenarios/performanceTest/performance-metrics-collection/4_ping_response_time/ping_response_time.robot",
                "Record response   edgex-device-rest",
                "# Record response   edgex-device-rest")
        # Remove service ping as service is not available in swagger but was available in docker container
        replace("TAF/testScenarios/performanceTest/performance-metrics-collection/4_ping_response_time/ping_response_time.robot",
                "${APP_SERVICE_RES_LIST}=  Ping API for service  app-service  ${APP_SERVICE_RULES_PORT}",
                "# ${APP_SERVICE_RES_LIST}=  Ping API for service  app-service  ${APP_SERVICE_RULES_PORT}")
        # Remove service ping as service is not available in swagger but was available in docker container
        replace("TAF/testScenarios/performanceTest/performance-metrics-collection/4_ping_response_time/ping_response_time.robot",
                "Record response   edgex-app-rules-engine",
                "# Record response   edgex-app-rules-engine")
        # Remove service ping as service is not available in swagger but was available in docker container
        replace("TAF/testScenarios/performanceTest/performance-metrics-collection/4_ping_response_time/ping_response_time.robot",
                "${DEVICE_VIRTUAL_RES_LIST}=  Ping API for service  device-virtual  ${DEVICE_VIRTUAL_PORT}",
                "# ${DEVICE_VIRTUAL_RES_LIST}=  Ping API for service  device-virtual  ${DEVICE_VIRTUAL_PORT}")
        # Remove service ping as service is not available in swagger but was available in docker container
        replace("TAF/testScenarios/performanceTest/performance-metrics-collection/4_ping_response_time/ping_response_time.robot",
                "Record response   edgex-device-virtual",
                "# Record response   edgex-device-virtual")
        # Replace Port in python file from 8443 to 8002, later on we can change it to 443
        replace("TAF/testCaseModules/keywords/performance-metrics-collection/PingResponse.py", "8443", "8002")
        # Replace Token method from BEARER to X-Auth-Token
        swap("TAF/testCaseModules/keywords/performance-metrics-collection/PingResponse.py",
             "header = {\"Authorization\": \"Bearer {}\".format(token)}",
             "header = {\"X-Auth-Token\": token}")
        # Imported data from configuration.py to profile_constant variable as in docker mode also this variable is setting
        add_data("TAF/testCaseModules/keywords/performance-metrics-collection/PingResponse.py",
                 "def show_aggregation_table_in_html():\n",
                 "profile_constant = __import__(\"TAF.config.performance-metrics.configuration\", fromlist=['configuration'])\n    SettingsInfo().add_name("
                 "'profile_constant', profile_constant)\n")
    if service == "3_resource_usage_with_autoevent" or service == "performance-metrics-collection":
        # Added dependent library in test robot file
        add_data("TAF/testScenarios/performanceTest/performance-metrics-collection/3_resource_usage_with_autoevent/resource_usage_with_autoevent.robot",
                 "Resource        TAF/testCaseModules/keywords/common/commonKeywords.robot\n",
                 "Variables       TAF/config/performance-metrics/configuration.py\n")


if __name__ == "__main__":
    main()

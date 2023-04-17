import json
import hashlib

def GenerateTEAL(filename):
    with open(filename) as f:
        abi = json.load(f)

    interface_selectors = {}
    method_selectors = {}

    # Compute selectors for all interfaces and methods
    for interface in abi['interfaces']:
        interface_selectors[interface['name']] = sum([ord(c) for c in interface['name']])
        for method in interface['methods']:
            # Compute selector based on method name and input types
            input_types = "".join(method['inputs'])
            method_selectors[method['name']] = sum([ord(c) for c in method['name']]) + sum([ord(c) for c in input_types])

    # Generate TEAL template
    template = ""

    # Add interface detection logic
    template += "txn ApplicationID\n"
    template += "int " + str(interface_selectors[abi['name']]) + "\n"
    template += "==" + "\n"
    template += "bnz interface_" + abi['name'] + "\n"
    template += "err" + "\n"

    # Add method routing logic for each interface
    for interface in abi['interfaces']:
        template += "interface_" + interface['name'] + ":" + "\n"
        template += "txn ApplicationArgs 0\n"
        template += "int " + str(method_selectors[interface['name'] + "." + interface['methods'][0]['name']]) + "\n"
        template += "==" + "\n"
        template += "bnz method_" + interface['name'] + "_" + interface['methods'][0]['name'] + "\n"
        template += "err" + "\n"
        for method in interface['methods'][1:]:
            template += "txn ApplicationArgs 0\n"
            template += "int " + str(method_selectors[interface['name'] + "." + method['name']]) + "\n"
            template += "==" + "\n"
            template += "bnz method_" + interface['name'] + "_" + method['name'] + "\n"
            template += "b interface_" + interface['name'] + "\n"
        # Add default error case if no method matches
        template += "err" + "\n"
        for method in interface['methods']:
            # Add method routing logic for each method
            template += "method_" + interface['name'] + "_" + method['name'] + ":" + "\n"
            # Add call config checks for this method
            for call_config in method.get('_call_config', []):
                if 'ApplicationID' in call_config:
                    template += "txn ApplicationID\n"
                    template += "int " + str(call_config['ApplicationID']) + "\n"
                    if call_config['ApplicationID_op'] == 'eq':
                        template += "==" + "\n"
                    else:
                        template += "!=" + "\n"
                    template += "bnz call_config_" + method['name'] + "_" + str(call_config['ApplicationID']) + "\n"
                if 'OnCompletion' in call_config:
                    template += "txn OnCompletion\n"
                    template += "int " + str(call_config['OnCompletion']) + "\n"
                    if call_config['OnCompletion_op'] == 'eq':
                        template += "==" + "\n"
                    else:
                        template += "!=" + "\n"
                    template += "bnz call_config_" + method['name'] + "_" + str(call_config['OnCompletion']) + "\n"
                if 'Sender' in call_config:
                    template += "txn Sender\n"
                    template += "addr " + str(call_config['Sender']) + "\n"
                    if call_config['Sender_op'] == 'eq':
                        template += "==" + "\n"
                    else:
                        template += "!=" + "\n"
                    template += "bnz call_config_" + method['name'] + "" + call_config['Sender'] + "\n"
            # Add custom logic for this method
            template += "# TODO: Add custom logic for " + interface['name'] + "." + method['name'] + "\n"
            template += "err" + "\n"
            # Add call config checks jump labels
            for call_config in method.get('call_config', []):
                template += "call_config" + method['name'] + "" + str(call_config.get('ApplicationID', '')) + "" + str(call_config.get('OnCompletion', '')) + "" + str(call_config.get('Sender', '')) + ":" + "\n"
            # Add custom logic for this call config
            template += "# TODO: Add custom logic for call config of " + interface['name'] + "." + method['name'] + "\n"
            template += "err" + "\n"
            return template
                 
                                              
                                              
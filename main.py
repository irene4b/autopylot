import argparse
from pyteslable import BLE

parser = argparse.ArgumentParser(description="Control Tesla vehicles using Bluetooth with autopylot.")
subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")
parser_pair = subparsers.add_parser("pair", help="Pair with a Tesla vehicle using a Bluetooth address")
parser_pair.add_argument("address", nargs="?", default=None, help="Bluetooth address of the vehicle")
parser_scan = subparsers.add_parser("scan", help="Scan for nearby Tesla vehicles")
parser_lock = subparsers.add_parser("lock", help="Lock the vehicle")
parser_unlock = subparsers.add_parser("unlock", help="Unlock the vehicle")
parser_trunk = subparsers.add_parser("trunk", help="Open the vehicle's trunk")
parser_frunk = subparsers.add_parser("frunk", help="Open the vehicle's front trunk")
parser_charge_open = subparsers.add_parser("charge open", help="Open the vehicle's charge port")
parser_charge_close = subparsers.add_parser("charge close", help="Close the vehicle's charge port")
parser_check_vin = subparsers.add_parser("check", help="Check the VIN for compatibility with the BLE protocol")
parser_check_vin.add_argument("vin", type=str, help="The VIN to be checked")

def check_vin_compatibility(vin):
    INCOMPATIBLE_DRIVE_UNITS = ["1", "2", "3", "4"]
    COMPATIBLE_MODELS = ["3", "Y"]
    
    model = vin[3]
    drive_unit = vin[7]
    model_year = vin[9]
    
    if model_year <= "L":
        if model in COMPATIBLE_MODELS:
            print(f"{vin} is compatible!")
        else:
            print(f"{vin} is incompatible!")
    elif model_year == "M":
        if drive_unit not in INCOMPATIBLE_DRIVE_UNITS:
            print(f"{vin} is compatible!")
        else:
            print(f"{vin} is incompatible!")
    else:
        print(f"{vin} is compatible!")

def handle_vehicle_command(command, vehicle):
    if command == "lock":
        vehicle.lock()
    elif command == "unlock":
        vehicle.unlock()
    elif command == "trunk":
        vehicle.open_trunk()
    elif command == "frunk":
        vehicle.open_frunk()
    elif command == "charge open":
        vehicle.open_charge_port()
    elif command == "charge close":
        vehicle.close_charge_port()

def main():
    args = parser.parse_args()
    tesla_ble = BLE("private_key.pem")

    vehicle = None

    if args.command == "scan":
        vehicles = tesla_ble.scan()
        if not vehicles:
            print("No vehicles found.")
            return
        for i, vehicle in enumerate(vehicles):
            print(f"{i}: {vehicle.name()} [{vehicle.address()}]")

    elif args.command == "check":
        if len(args.vin) != 17:
            print(f"{args.vin} is not a valid VIN.")
            return

        check_vin_compatibility(args.vin)

    
    elif args.command == "pair":
        if args.address:
            vehicle = tesla_ble.connect(args.address)
            if vehicle and vehicle.is_connected():
                print(f"Paired with {vehicle.name()} at {args.address}")
            else:
                print("Failed to connect.")
        else:
            vehicles = tesla_ble.scan()
            if not vehicles:
                print("No vehicles found.")
                return
            for i, vehicle in enumerate(vehicles):
                print(f"{i}: {vehicle.name()} [{vehicle.address()}]")
            choice = int(input("Enter choice: "))
            selected_vehicle = vehicles[choice]
            selected_vehicle.connect()
            if selected_vehicle.is_connected():
                print(f"Paired with {selected_vehicle.name()}")

    else:
        print("Please scan and pair with a vehicle first.")
        return

    while True:
        command = input("Enter a command (type 'help' for options, 'exit' to quit): ").lower().replace(' ', '_')
        if command == "exit":
            break
        elif command == "help":
            parser.print_help()
        elif command == "check":
            vin = input("Enter a VIN to check: ")
            check_vin_compatibility(vin)
        else:
            handle_vehicle_command(command, vehicle)

    if vehicle:
        print("Disconnecting...")
        vehicle.disconnect()
        print("Vehicle disconnected successfully")

if __name__ == "__main__":
    main()

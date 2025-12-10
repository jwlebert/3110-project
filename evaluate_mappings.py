import xml.etree.ElementTree as ET
import os
import csv

# The list of files to check
FILES_TO_TEST = [
    "asdf", "ASTResolving", "ArrayReference", "BaseTypes",
    "BuildPathsPropertyPage", "CPListLabelProvider",
    "CompilationUnitDocumentProvider", "DeltaProcessor",
    "DialogCustomize", "DirectoryDialog", "DoubleCache",
    "FontData", "GC", "GC2", "JavaCodeScanner",
    "JavaModelManager", "JavaPerspectiveFactory",
    "PluginSearchScope", "RefreshLocal", "ResourceCompareInput", 
    "ResourceInfo", "SaveManager", "TabFolder"
]

def parse_mapping_xml(xml_file):
    if not os.path.exists(xml_file):
        return None
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except ET.ParseError:
        return None

    file_mappings = {}
    for version in root.findall("VERSION"):
        v_num = version.get("NUMBER")
        v_map = {}
        for location in version.findall("LOCATION"):
            try:
                orig = int(location.get("ORIG"))
                new_start = int(location.get("NEW"))
                targets = {new_start}
                for alt in location.findall("ALT"):
                    targets.add(int(alt.get("NEW")))
                v_map[orig] = targets
            except (ValueError, TypeError):
                continue 
        file_mappings[v_num] = v_map
    return file_mappings

def main():
    gt_dir = os.path.join("datasets", "provided")
    gen_dir = "output"
    
    # List to store rows for CSV
    csv_rows = []
    # Header row
    csv_rows.append(["Test File", "Accuracy (%)", "Correct Matches", "Total Mappings"])

    global_total = 0
    global_correct = 0

    print(f"{'TEST FILE':<35} | {'ACCURACY':<10} | {'MATCHES':<15}")
    print("-" * 70)

    for filename in FILES_TO_TEST:
        gt_path = os.path.join(gt_dir, f"{filename}.xml")
        gen_path = os.path.join(gen_dir, f"{filename}.xml")

        gt_data = parse_mapping_xml(gt_path)
        gen_data = parse_mapping_xml(gen_path)

        # Default values for missing files
        acc_str = "N/A"
        file_correct = 0
        file_total = 0

        if gt_data and gen_data:
            for v_num, gt_mappings in gt_data.items():
                if v_num not in gen_data: continue
                gen_mappings = gen_data[v_num]
                for orig_line, gt_targets in gt_mappings.items():
                    file_total += 1
                    if orig_line in gen_mappings:
                        if gt_targets == gen_mappings[orig_line]:
                            file_correct += 1
            
            if file_total > 0:
                acc_val = (file_correct / file_total * 100)
                acc_str = f"{acc_val:.2f}"
            else:
                acc_str = "0.00"

            print(f"{filename:<35} | {acc_str + '%':<10} | {file_correct}/{file_total}")
        else:
            print(f"{filename:<35} | {'MISSING':<10} | N/A")

        # Add to CSV data
        csv_rows.append([filename, acc_str, file_correct, file_total])

        global_total += file_total
        global_correct += file_correct

    # Calculate Overall Stats
    print("-" * 70)
    overall_acc = (global_correct / global_total * 100) if global_total > 0 else 0
    print(f"FINAL ACCURACY: {overall_acc:.2f}%")
    
    # Append total row to CSV data
    csv_rows.append([]) # Empty row for spacing
    csv_rows.append(["TOTAL / AVERAGE", f"{overall_acc:.2f}", global_correct, global_total])

    # Write to CSV file
    csv_filename = "results.csv"
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(csv_rows)
    
    print(f"\n[Success] Results written to {csv_filename}")

if __name__ == "__main__":
    main()
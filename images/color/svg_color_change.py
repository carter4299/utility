import xml.etree.ElementTree as ET
from PIL import Image
import io
import cairosvg
from collections import Counter
import os
#FF4F44
def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def list_svgs_in_assets():
    all_files = os.listdir('assets')
    svg_files = [f for f in all_files if f.endswith('.svg')]
    return svg_files

def main():
    new_hex_color = input("Enter a new hex color (or 0 to exit): ")
    if new_hex_color == '0':
        print("Goodbye!")
        return
    if not new_hex_color.startswith('#'):
        new_hex_color = '#' + new_hex_color
    print(f"You entered: {new_hex_color}")
    correct = input("Is this correct? (y/n): ")
    if correct.lower() == 'y':
        pass
    else:
        main()
    while True:
        clear_terminal()
        svg_files = list_svgs_in_assets()
        print("Available SVG files:")
        for idx, svg_file in enumerate(svg_files, start=1):
            print(f"({idx})- {svg_file}")
        print('My Color')
        print(new_hex_color)

        try:
            choice = int(input("\nChoose a SVG file by entering its number (or 0 to exit): "))
            if choice == 0:
                print("Goodbye!")
                break
            if 0 < choice <= len(svg_files):
                selected_svg = svg_files[choice - 1]
                print(f"You selected: {selected_svg}")
                _p = os.path.join(os.getcwd(),f'assets/{selected_svg}')
                change_svg_color(selected_svg,_p, new_hex_color, most_frequent_color(_p))
                display_svg(f'new_{selected_svg}')
                
                input("Press Enter to continue...")
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def most_frequent_color2(svg_path):
    tree = ET.parse(svg_path)
    root = tree.getroot()
    namespaces = {'ns': 'http://www.w3.org/2000/svg'}

    stroke_colors = [elem.attrib['stroke'] for elem in root.findall(".//*[@stroke]", namespaces=namespaces) if elem.attrib['stroke'].startswith('#')]
    color_counts = Counter(stroke_colors)

    if color_counts:
        return color_counts.most_common(1)[0][0], 0
    else:
        return None, None 
    
def most_frequent_color(svg_path):
    r, t = try_fill_method1(svg_path)
    if r and t:
        return r, t
    
    _r, _t = try_fill_method2(svg_path)
    if _r and _t:
        return _r, _t

    return most_frequent_color2(svg_path)
    
def try_fill_method1(svg_path):
    tree = ET.parse(svg_path)
    root = tree.getroot()
    namespaces = {'ns': 'http://www.w3.org/2000/svg'}
    
    colors = [elem.attrib['fill'] for elem in root.findall(".//*[@fill]", namespaces=namespaces)]
    color_counts = Counter(colors)

    if color_counts:
        return color_counts.most_common(1)[0][0], 1
    else:
        return None, None
    
def try_fill_method2(svg_path):
    tree = ET.parse(svg_path)
    root = tree.getroot()
    namespaces = {'ns': 'http://www.w3.org/2000/svg'}
    
    root_fill = root.get('fill')
    colors = [root_fill] if root_fill else []
    colors += [elem.attrib['fill'] for elem in root.findall(".//*[@fill]", namespaces=namespaces)]
    
    color_counts = Counter(colors)

    if color_counts:
        return color_counts.most_common(1)[0][0], 2
    else:
        return None, None


def change_svg_color(f_name, svg_path, new_hex_color, most_frequent_color):
    old_hex_color, x = most_frequent_color
    print(f"new_hex_color: {new_hex_color}")
    print(f"old_hex_color: {old_hex_color}")
    tree = ET.parse(svg_path)
    root = tree.getroot()
    namespaces = {'ns': 'http://www.w3.org/2000/svg'}
        
    if x == 0:
        print("stroke")
        for elem in root.findall(".//*[@stroke]", namespaces=namespaces):
            if elem.attrib['stroke'] == old_hex_color:
                elem.attrib['stroke'] = new_hex_color
    elif x == 1:
        print("fill")
        for elem in root.findall(".//*[@fill]", namespaces=namespaces):
            if elem.attrib['fill'] == old_hex_color:
                elem.attrib['fill'] = new_hex_color
    elif x == 2:
        print("root fill")
        if root.get('fill') == old_hex_color:
            root.set('fill', new_hex_color)


    
    tree.write(f'new_{f_name}')

def display_svg(svg_path):
    Image.open(io.BytesIO(cairosvg.svg2png(url=svg_path))).show()



if __name__ == "__main__":
    main()

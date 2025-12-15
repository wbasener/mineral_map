# Leaflet.Control.Appearance Integration Script

## Overview

This Python script (`add_appearance_control.py`) automatically modifies your `index.html` file to replace the standard Leaflet layer control with the more advanced **Leaflet.Control.Appearance** plugin, which provides:

- **Opacity control** - Dynamically adjust layer transparency
- **Color modification** - Change layer colors on the fly
- **Layer removal** - Remove layers from the map interactively
- **Enhanced UI** - Better user experience for managing multiple overlay layers

## What the Script Does

The script performs the following modifications:

### 1. **Creates a Backup**
   - Generates a timestamped backup of your original `index.html`
   - Format: `index.backup_YYYYMMDD_HHMMSS.html`

### 2. **Adds Plugin References**
   - Inserts the Leaflet.Control.Appearance JavaScript library from CDN
   - Adds the corresponding CSS stylesheet
   - Placed after existing Leaflet library includes in the `<head>` section

### 3. **Modifies GeoJSON Layer Definitions**
   - Adds `name`, `color`, and `opacity` properties to each of the 18 mineral abundance layers
   - Extracts color information from existing styler functions
   - Extracts layer names from the layer control configuration

### 4. **Reorganizes Layers**
   - Creates three JavaScript arrays:
     - `baseLayers` - Array of 4 tile layers (OpenStreetMap, Topographic, Light Map, Satellite)
     - `uneditableOverlays` - Empty array (can be customized if needed)
     - `overlays` - Array of 18 editable mineral abundance GeoJSON layers

### 5. **Replaces Layer Control**
   - Removes the old `L.control.layers()` implementation
   - Replaces it with `L.control.appearance()` with the following options:
     - `position: 'topright'` - Control positioned in top-right corner
     - `radioCheckbox: true` - Radio buttons for base layers, checkboxes for overlays
     - `layerName: true` - Display layer names
     - `opacity: true` - Enable opacity control
     - `color: true` - Enable color modification
     - `remove: true` - Enable layer removal

### 6. **Generates Log File**
   - Creates a detailed modification log
   - Timestamp and list of all changes made

## Usage

### Prerequisites
- Python 3.6 or higher
- The script must be in the same directory as `index.html`

### Running the Script

```bash
# From the mineral_map directory
python add_appearance_control.py
```

Or on some systems:

```bash
python3 add_appearance_control.py
```

### Expected Output

```
Starting Leaflet.Control.Appearance integration...

Created backup: index.backup_20251215_143022.html
Loaded index.html (7894523 characters)
Found 4 tile layers and 18 GeoJSON layers
Added Leaflet.Control.Appearance plugin references
Modified 18 GeoJSON layers with appearance options
Replaced L.control.layers() with L.control.appearance()
Saved modified content to index.html

Log saved to: modification_log_20251215_143022.txt

==================================================
Modification complete!
Original file backed up to: index.backup_20251215_143022.html
Modified file: index.html
==================================================
```

## After Running the Script

1. **Test the modified HTML file**
   - Open `index.html` in a web browser
   - Verify that the map loads correctly
   - Check that the new Appearance control is visible in the top-right corner

2. **Test the new features**
   - Toggle base layers using radio buttons
   - Toggle overlay layers using checkboxes
   - Adjust opacity sliders for each overlay
   - Try changing layer colors
   - Test the remove functionality

3. **If something goes wrong**
   - The original file is safely backed up
   - Simply replace `index.html` with the backup file
   - Review the modification log to understand what changed

## Reverting Changes

If you need to revert to the original version:

```bash
# Copy the backup back (replace timestamp with your actual backup timestamp)
cp index.backup_20251215_143022.html index.html
```

On Windows:
```cmd
copy index.backup_20251215_143022.html index.html
```

## Technical Details

### Layer Structure Required by Plugin

The Leaflet.Control.Appearance plugin requires layers to have specific options:

```javascript
{
  name: "Layer display name",
  color: "#hexcolor",
  opacity: 0.6
}
```

The script automatically extracts these from your existing layer definitions:
- **name**: From the layer control mapping (e.g., "Alunite abundance > 0.1)")
- **color**: From the `fillColor` property in each layer's styler function
- **opacity**: From the `fillOpacity` property in each layer's styler function

### Plugin Source

The script uses the Leaflet.Control.Appearance plugin from:
- **GitHub**: https://github.com/Kanahiro/Leaflet.Control.Appearance
- **CDN**: jsdelivr (loads from GitHub repository)

**Note**: This repository is archived (read-only as of February 2025), so no future updates will be available.

## Customization

After running the script, you can manually customize the appearance control by editing the configuration in `index.html`:

```javascript
var appearanceControl = L.control.appearance(
    baseLayers,
    uneditableOverlays,
    overlays,
    {
        position: 'topright',        // Change position: 'topleft', 'bottomright', etc.
        radioCheckbox: true,         // Set to false to use checkboxes for all layers
        layerName: true,             // Set to false to hide layer names
        opacity: true,               // Set to false to disable opacity control
        color: true,                 // Set to false to disable color modification
        remove: true                 // Set to false to disable layer removal
    }
);
```

## Troubleshooting

### Script Errors
- **"index.html not found"**: Make sure the script is in the same directory as index.html
- **Permission denied**: Ensure you have write permissions in the directory

### After Modification
- **Map doesn't load**: Check browser console (F12) for JavaScript errors
- **Control doesn't appear**: Verify the plugin CDN links are accessible
- **Layers don't respond**: Check that layer options were added correctly

## Support

For issues with:
- **This script**: Check the modification log file for details
- **The plugin itself**: See https://github.com/Kanahiro/Leaflet.Control.Appearance
- **Leaflet.js**: See https://leafletjs.com/

## License

This script is provided as-is for modifying Leaflet.js maps to use the Control.Appearance plugin.

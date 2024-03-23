# BetterStats
![2024-03-23 12_39_45-Blender](https://github.com/ssnd292/BetterStats/assets/3914410/3978be35-ef4b-486c-8eb3-4b354dab9d7b)


Adds a new Statistics overlay in Blender for more in-depth mesh data stats. It was always a pain for me to explain to other artists why the vertex normal count is more important than just the vertex count. While in Blender you can visually show them, they are hard to track. My own goal was always to have another way to show the total count of them when doing model optimization, and this is where the idea for this addon came from.

After installing, it can be activated and deactivated in the Viewport Overlays. You can also adjust the font size and color to your liking.
![2024-03-23 11_25_21-Blender](https://github.com/ssnd292/BetterStats/assets/3914410/5003e909-8157-4cf5-ac5c-a09d5840dd89)


Currently the limitation is that it only updates when you are working on object mode, as there are now handlers yet when working in editmode (unfortunately it seems like the original statistics have access to different information than to what is exposed to us)

Once again big thanks to https://github.com/sleepermt for all the help.

Please message me here or on twitter https://twitter.com/ssnd292 if you have any issues or wishes.


Currently, there are two major issues:
- Depending on your monitor resolution and blender window size, the overlay may be behind other UI elements or even off screen
- In very performance heavy scenes, the addon can be slow to calculate the stats

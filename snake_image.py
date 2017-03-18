import numpy as np
import pygame
import math
import colorsys



# light: [light_dir, ambient, diffuse, specular, shininess]
def createImage(diffuse_map, normal_map, specular_map, emissive_map, hue_mask, color, light):

    def readNormal(normal_map, pos):
        if normal_map != None:
            n = (np.array(normal_map.get_at(pos)[:3]) / 255.0) * 2 - 1
            norm = np.linalg.norm(n)
            return (n / norm) if norm else n
        else:
            return np.array((0,0,0))


    def readColor(diffuse_map, new_color_mask, new_color, pos):
        if diffuse_map != None:
            c = diffuse_map.get_at(pos)
            alpha = c[3]/255 if len(c) >= 4 else 1.0
            color = np.array(c[:3])/255  
        else:
            alpha = 1.0
            color = np.array((1,1,1))  
        
        if new_color_mask != None:
            mask = max(new_color_mask.get_at(pos)) / 255
            if mask > 0:
                newH, newS, newV = colorsys.rgb_to_hsv(*(new_color/255))
                oldH, oldS, oldV = colorsys.rgb_to_hsv(*color)
                if oldS*newS == 0:
                    H = oldH
                else:
                    dH = newH-oldH
                    if dH < -0.5: dH += 1
                    elif dH > 0.5: dH -= 1
                    H = np.interp(mask, [0,1], [oldH, oldH+dH])
                    if H < 0: H += 1
                    elif H >= 1: H -= 1
                S = np.interp(mask, [0,1], [1, newS]) * oldS
                V = np.interp(mask, [0,1], [1, newV]) * oldV
                color = np.array(colorsys.hsv_to_rgb(H, S, V))

        return (color, alpha)
            

    def readEmissive(emissive_map, pos):
        if emissive_map != None:
            return min(emissive_mask.get_at(pos)) / 255
        else:
            return 0

    def readSpecular(specular_map, pos):
        if specular_map != None:
            return min(specular_map.get_at(pos)) / 255
        else:
            return 1.0
    
    image_out = pygame.Surface(diffuse_map.get_size(), pygame.SRCALPHA)

    H = np.array((0,0,1)) - light["dir"]
    H /= np.linalg.norm(H)

    for i in range(image_out.get_width()):
        for j in range(image_out.get_height()):
            # (x,y,z)
            normal = readNormal(normal_map, (i, j))
            # (r,g,b), alpha
            color, alpha = readColor(diffuse_map, hue_mask, color, (pos))
            # (r,g,b)
            specular = readSpecular(specular_map, i, j) * light["specular"]
            # i
            emissive = readEmissive(emissive_map, i, j)

            spec = (max(0.0, np.dot(normal, H)) ** light["shininess"]) * specular if -np.dot(normal, light["dir"]) > 0 else 0.0
            diff = max(0.0, -np.dot(normal, light["dir"])) * light["diffuse"]
            c = (diff + light["ambient"] + emissive) * color + spec
            
            r, g, b = np.int_(np.clip(c, 0.0, 1.0) * 255)
            image_out.set_at((i,j), (r, g, b, alpha))

    return image_out

if __name__ == "__main__":
    light={"dir":np.array((0,-3/5,-4/5)),
            "ambient": np.array((0.5,0.5,0.5)),
            "diffuse": np.array((0.5,0.5,0.5)),
            "specular": np.array((0.3,0.3,0.3)),
            "shininess": 8
            }
    img = pygame.image.load("assets/images/apple-worm.png")
    pygame.transform.rotate(img, 10)

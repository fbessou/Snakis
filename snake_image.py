import numpy as np
import pygame
import math



# light: [light_dir, ambient, diffuse, specular, shininess]
def createImage(diffuse_map, normal_map, specular_map, emissive_map, hue_mask, color, light):

    def readNormal(normal_map, pos):
        if normal_map != None:
            n = (np.array(normal_map.get_at(pos)[:3]) / 255.0) * 2 - 1
            norm = np.linalg.norm(n)
            return (n / norm) if norm else n
        else:
            return np.array((0,0,0))


    def readColor(diffuse_map, hue_mask, hue_color, pos):
        if diffuse_map != None:
            # D if min(hue.get_at(pos)) == 0 else D.mix(hue_color)
            c = diffuse_map.get_at(pos)
            alpha = c[3]/255 if len(c) >= 4 else 1.0
            return (np.array(c[:3])/255, alpha)  
        else:
            return (np.array((1,1,1)), 1.0)

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
    pygame.transform.rotate(img, 10*i)

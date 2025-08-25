import math, time, sys

WIDTH, HEIGHT = 100, 40   
SCALE = 12                   
STEP = 0.25                 
FRAME_DELAY = 0.03           
CHARSET = "0123456789"       
LIGHT_DIR = (0.5, 0.5, 1.0)  

def norm(v):
    x,y,z = v
    m = math.sqrt(x*x+y*y+z*z) or 1.0
    return (x/m, y/m, z/m)

Ld = norm(LIGHT_DIR)

def rotate(p, ax, ay, az):
    x,y,z = p
    # Rx
    cx,sx = math.cos(ax), math.sin(ax)
    y,z = y*cx - z*sx, y*sx + z*cx
    # Ry
    cy,sy = math.cos(ay), math.sin(ay)
    x,z = x*cy + z*sy, -x*sy + z*cy
    # Rz
    cz,sz = math.cos(az), math.sin(az)
    x,y = x*cz - y*sz, x*sz + y*cz
    return (x,y,z)

def project(p, fov=3.5, dist=6.0):
    x,y,z = p
    z += dist
    if z <= 0.1: z = 0.1
    k = fov / z
    u = int(WIDTH  * 0.5 + x * k * SCALE)
    v = int(HEIGHT * 0.5 - y * k * SCALE)
    return u, v, z

def shade(intensity):
    # intensity у [0,1] -> індекс у CHARSET
    intensity = max(0.0, min(1.0, intensity))
    idx = int(intensity * (len(CHARSET)-1) + 0.5)
    return CHARSET[idx]

# Генерація точок на 6 гранях куба та їх нормалей
def cube_points(step=STEP):
    pts = []
    rng = [i*step-1 for i in range(int(2/step)+1)]
    for t in rng:
        for s in rng:
            
            pts.extend([
                (( 1,  s,  t), ( 1, 0, 0)),
                ((-1,  s,  t), (-1, 0, 0)),
                (( s,  1,  t), ( 0, 1, 0)),
                (( s, -1,  t), ( 0,-1, 0)),
                (( s,  t,  1), ( 0, 0, 1)),
                (( s,  t, -1), ( 0, 0,-1)),
            ])
    return pts

PTS = cube_points()

sys.stdout.write("\x1b[2J\x1b[?25l")
sys.stdout.flush()

ax = ay = az = 0.0
try:
    while True:
        # буфери кадру
        zbuf = [[1e9]*WIDTH for _ in range(HEIGHT)]
        fb   = [[" "]*WIDTH for _ in range(HEIGHT)]

        for (x,y,z), n in PTS:
            # обертання точки і нормалі
            X,Y,Z = rotate((x,y,z), ax, ay, az)
            Nx,Ny,Nz = rotate(n, ax, ay, az)

            # просте відсікання ззаду (back-face) — малюємо тільки "видимі" грані
            if Nx*Ld[0] + Ny*Ld[1] + Nz*Ld[2] <= 0:
                continue

            u,v,depth = project((X,Y,Z))
            if 0 <= u < WIDTH and 0 <= v < HEIGHT:
                if depth < zbuf[v][u]:  # z-buffer
                    zbuf[v][u] = depth
                    # ламбертівське освітлення
                    l = max(0.0, min(1.0, (Nx*Ld[0] + Ny*Ld[1] + Nz*Ld[2])))
                    fb[v][u] = shade(l)

        sys.stdout.write("\x1b[H")
        for row in fb:
            sys.stdout.write("".join(row) + "\n")
        sys.stdout.flush()

        # обертання
        ax += 0.04
        ay += 0.06
        az += 0.02
        time.sleep(FRAME_DELAY)

except KeyboardInterrupt:
    pass
finally:

    sys.stdout.write("\x1b[?25h\n")
    sys.stdout.flush()

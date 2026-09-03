import numpy as np

def crop_pointscloude(data_path):
    #in_path = r"G:\TK-set\2.1data\20260526-4\8C25F点云分层1.67cm\2026-05-26_17-02-19\AllGeoPoints.txt"
    #out_path = r"G:\TK-set\2.1data\20260526-4\8C25F点云分层1.67cm\2026-05-26_17-02-19\out.txt"
    in_path=data_path+r'\AllGeoPoints.txt'
    out_path=data_path+r'\crop_AllGeoPoints.txt'

    xmin, xmax = -10.893, -3.536
    ymin, ymax = -1.353, 3.532
    zmin, zmax = 6.361, 6.409

    print(f"加载: {in_path}")
    data = np.loadtxt(in_path)
    print(f"原始点数: {len(data)}")

    points = data[:, :3]
    mask = (
        (points[:, 0] >= xmin) & (points[:, 0] <= xmax) &
        (points[:, 1] >= ymin) & (points[:, 1] <= ymax) &
        (points[:, 2] >= zmin) & (points[:, 2] <= zmax)
    )

    cropped = data[mask]
    print(f"截取范围: X [{xmin}, {xmax}], Y [{ymin}, {ymax}], Z [{zmin}, {zmax}]")
    print(f"截取后点数: {len(cropped)} ({len(cropped) / len(data):.1%})")

    #np.savetxt(out_path+'crop_AllGeoPoints.txt', cropped, fmt='%.6f')
    np.savetxt(out_path , cropped, fmt='%.6f')
    print(f"已保存: {out_path}")


if __name__=="__main__":
    # in_path = r"G:\TK-set\2.1data\20260526-4\5B121-0\2026-05-26_16-55-41\AllGeoPoints.txt"
    in_path = r"G:\TK-set\2.1data\20260731\8cc53\2026-07-31_16-17-07"
    crop_pointscloude(in_path)
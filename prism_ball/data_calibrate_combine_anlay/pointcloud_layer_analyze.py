import numpy as np
import open3d as o3d
import sys
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
from pathlib import Path


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


def load_pointcloud(path):
    data = np.loadtxt(path)
    return data


def fit_plane(points):
    center = points.mean(axis=0)
    centered = points - center
    cov = centered.T @ centered / len(points)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)
    normal = eigenvectors[:, 0]
    d = -normal @ center
    return normal, d


def estimate_thickness(points):
    if len(points) < 4:
        return 0.0, 0.0, 0.0

    normal, d = fit_plane(points)
    distances = np.abs(points @ normal + d)

    thickness_range = float(distances.max() - distances.min())
    thickness_rmse = float(np.sqrt(np.mean(distances ** 2)))
    p95, p5 = np.percentile(distances, [95, 5])
    thickness_p95 = float(p95 - p5)

    return thickness_range, thickness_rmse, thickness_p95


def detect_layering_histogram(points):
    if len(points) < 10:
        return False, 0, []

    normal, d = fit_plane(points)
    signed_distances = points @ normal + d

    total_range = float(signed_distances.max() - signed_distances.min())

    bin_width = max(total_range * 0.002, 0.001)
    n_bins = max(20, min(1000, int(total_range / bin_width)))
    n, bins = np.histogram(signed_distances, bins=n_bins)
    bin_centers = (bins[:-1] + bins[1:]) / 2

    sigma = max(1.0, n_bins / 100)
    smoothed = gaussian_filter1d(n.astype(float), sigma=sigma)

    min_dist = max(int(n_bins * 0.03), 1)
    all_peaks, _ = find_peaks(smoothed, distance=min_dist)
    if len(all_peaks) < 2:
        return False, 0, []

    heights = smoothed[all_peaks]
    sorted_h = np.sort(heights)[::-1]

    gaps = np.diff(sorted_h)
    if len(gaps) == 0:
        return False, 0, []

    max_gap_idx = np.argmax(gaps)
    max_gap = gaps[max_gap_idx]
    min_gap_threshold = max(sorted_h[0] * 0.05, 3.0)

    if max_gap < min_gap_threshold:
        return False, 0, []

    significant_h = sorted_h[:max_gap_idx + 1]
    significant_peaks = [p for p in all_peaks if smoothed[p] >= significant_h[-1]]

    if len(significant_peaks) < 2:
        return False, 0, []

    main_idx = np.argmax(smoothed[significant_peaks])
    main_pos = bin_centers[significant_peaks[main_idx]]

    result = []
    for p in significant_peaks:
        pos = bin_centers[p]
        gap = abs(pos - main_pos)
        if gap > max(total_range * 0.01, 0.006):
            result.append((pos, smoothed[p]))

    if len(result) >= 1:
        all_layers = [(main_pos, smoothed[significant_peaks[main_idx]])] + result
        return True, len(all_layers), all_layers

    return False, 0, []


def detect_layering_dbscan(points):
    if len(points) < 10:
        return False, 0, [], []

    diag = np.linalg.norm(points.max(axis=0) - points.min(axis=0))
    voxel_size = max(diag * 0.005, 0.05)

    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd_down = pcd.voxel_down_sample(voxel_size)
    points_down = np.asarray(pcd_down.points)

    scaler = StandardScaler()
    points_norm = scaler.fit_transform(points_down)

    best_n = 0
    best_labels = None
    for eps in [0.3, 0.5, 0.8, 1.0, 1.5, 2.0, 3.0]:
        clustering = DBSCAN(eps=eps, min_samples=5, n_jobs=-1).fit(points_norm)
        labels = clustering.labels_
        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        noise_ratio = list(labels).count(-1) / len(labels)
        if n_clusters >= 2 and noise_ratio < 0.3 and n_clusters > best_n:
            best_n = n_clusters
            best_labels = labels

    if best_n < 2:
        return False, 0, [], []

    min_cluster_size = max(10, len(points_down) * 0.002)
    cluster_info = []
    for label in sorted(set(best_labels)):
        if label < 0:
            continue
        mask = best_labels == label
        count = int(mask.sum())
        if count < min_cluster_size:
            continue
        cluster_pts = points_down[mask]
        info = {
            'count': count,
            'centroid': cluster_pts.mean(axis=0),
        }
        cluster_info.append(info)

    if len(cluster_info) < 2:
        return False, 0, [], []

    cluster_info.sort(key=lambda x: x['count'], reverse=True)
    centroids = np.array([c['centroid'] for c in cluster_info])
    dists = []
    for i in range(len(centroids)):
        for j in range(i + 1, len(centroids)):
            dists.append(float(np.linalg.norm(centroids[i] - centroids[j])))
    return True, len(cluster_info), cluster_info, dists


def detect_layering_by_slice(points, n_slices=20):
    if len(points) < 100:
        return False, 0, []

    axis_ranges = points.ptp(axis=0)
    main_axis = int(np.argmax(axis_ranges))

    axis_labels = ['X', 'Y', 'Z']
    height_axis = 2
    if main_axis == 2:
        height_axis = 1

    sorted_idx = np.argsort(points[:, main_axis])
    sorted_pts = points[sorted_idx]

    slice_size = max(len(points) // n_slices, 50)
    layered_cells = 0
    total_cells = 0
    all_heights = []

    for start in range(0, len(sorted_pts), slice_size):
        end = min(start + slice_size, len(sorted_pts))
        slice_pts = sorted_pts[start:end]
        if len(slice_pts) < 30:
            continue

        total_cells += 1
        h = slice_pts[:, height_axis]

        n_bins = min(50, len(slice_pts) // 5)
        if n_bins < 5:
            continue
        hist, bins = np.histogram(h, bins=n_bins)
        smoothed = gaussian_filter1d(hist.astype(float), sigma=1.0)
        peaks, _ = find_peaks(smoothed, distance=max(3, n_bins // 8))

        if len(peaks) >= 2:
            peak_h = smoothed[peaks]
            sorted_idx = np.argsort(peak_h)[::-1]
            if peak_h[sorted_idx[1]] > peak_h[sorted_idx[0]] * 0.05:
                bc = (bins[:-1] + bins[1:]) / 2
                peak_pos = bc[peaks]
                gap = abs(peak_pos[sorted_idx[0]] - peak_pos[sorted_idx[1]])
                h_range = h.max() - h.min()
                if gap > max(h_range * 0.02, 0.006):
                    layered_cells += 1
                    all_heights.append(float(gap))

    if total_cells == 0:
        return False, 0, []

    layer_ratio = layered_cells / total_cells
    if layer_ratio > 0.15 and all_heights:
        avg_gap = np.mean(all_heights)
        min_gap = np.min(all_heights)
        max_gap = np.max(all_heights)
        return True, layered_cells, [layer_ratio, total_cells, avg_gap, min_gap, max_gap, axis_labels[main_axis], axis_labels[height_axis]]

    return False, 0, []


def analyze_pointcloud(data_path):
    file_path=  data_path + r'\crop_AllGeoPoints.txt'
    data = load_pointcloud(file_path)
    points = data[:, :3] if data.shape[1] >= 3 else data
    analyze_results=[]
    print(f"加载点云: {file_path}")
    print(f"点数: {len(points)}")
    analyze_results.append("\n厚度分析:")
    print(f"\n厚度分析:")
    thickness_range, thickness_rmse, thickness_p95 = estimate_thickness(points)
    print(f"  最大范围厚度: {thickness_range:.4f} m")
    print(f"  均方根厚度:   {thickness_rmse:.4f} m")
    print(f"  90% 置信厚度: {thickness_p95:.4f} m")
    analyze_results.append(f"  最大范围厚度: {thickness_range:.4f} m")
    analyze_results.append(f"   均方根厚度:   {thickness_rmse:.4f} m")
    analyze_results.append(f"   90% 置信厚度: {thickness_p95:.4f} m")


    has_any = False

    print(f"\n分层检测 (切片分析, 沿最长轴切片):")
    analyze_results.append(f"\n分层检测 (切片分析, 沿最长轴切片):")
    has_layers_s, n_layers_s, info_s = detect_layering_by_slice(points)
    if has_layers_s:
        has_any = True
        ratio, total, avg_gap, min_gap, max_gap, main_ax, h_ax = info_s
        print(f"  检测结果: 存在分层! ({n_layers_s}/{int(total)} 个切片检测到多层)")
        print(f"    分层切片占比: {ratio:.1%}, 层间距: 均值 {avg_gap:.4f} m, 范围 [{min_gap:.4f} m, {max_gap:.4f} m]")
        print(f"    切片方向: {main_ax}, 高度方向: {h_ax}")
        analyze_results.append(f"  检测结果: 存在分层! ({n_layers_s}/{int(total)} 个切片检测到多层)")
        analyze_results.append(f"    分层切片占比: {ratio:.1%}, 层间距: 均值 {avg_gap:.4f} m, 范围 [{min_gap:.4f} m, {max_gap:.4f} m]")
        analyze_results.append(f"    切片方向: {main_ax}, 高度方向: {h_ax}")
    else:
        print(f"  检测结果: 未检测到明显分层")
        analyze_results.append(f"  检测结果: 未检测到明显分层")

    print(f"\n分层检测 (法线方向直方图):")
    analyze_results.append(f"\n分层检测 (法线方向直方图):")
    has_layers_h, n_layers_h, layers_h = detect_layering_histogram(points)
    if has_layers_h:
        has_any = True
        print(f"  检测结果: 存在分层! ({n_layers_h} 层)")
        analyze_results.append(f"  检测结果: 存在分层! ({n_layers_h} 层)")
        for i, (pos, h) in enumerate(layers_h):
            print(f"    层 {i+1}: 深度 {pos:.4f} m, 峰值强度 {h:.0f}")
            analyze_results.append(f"    层 {i+1}: 深度 {pos:.4f} m, 峰值强度 {h:.0f}")
    else:
        print(f"  检测结果: 未检测到明显分层")
        analyze_results.append(f"  检测结果: 未检测到明显分层")

    print(f"\n分层检测 (DBSCAN 聚类):")
    analyze_results.append(f"\n分层检测 (DBSCAN 聚类):")
    has_layers_d, n_layers_d, clusters, dists_d = detect_layering_dbscan(points)
    if has_layers_d:
        has_any = True
        print(f"  检测结果: 存在分层! ({n_layers_d} 层)")
        analyze_results.append(f"  检测结果: 存在分层! ({n_layers_d} 层)")
        for i, c in enumerate(clusters):
            print(f"    层 {i+1}: {c['count']} 点, 中心 ({c['centroid'][0]:.2f}, {c['centroid'][1]:.2f}, {c['centroid'][2]:.2f}) m")
            analyze_results.append(f"    层 {i+1}: {c['count']} 点, 中心 ({c['centroid'][0]:.2f}, {c['centroid'][1]:.2f}, {c['centroid'][2]:.2f}) m")
        if dists_d:
            print(f"    层间距离: 均值 {np.mean(dists_d):.4f} m, 范围 [{np.min(dists_d):.4f} m, {np.max(dists_d):.4f} m]")
            analyze_results.append(f"    层间距离: 均值 {np.mean(dists_d):.4f} m, 范围 [{np.min(dists_d):.4f} m, {np.max(dists_d):.4f} m]")
    else:
        print(f"  检测结果: 未检测到明显分层")
        analyze_results.append(f"  检测结果: 未检测到明显分层")

    print(f"\n结论: {'存在分层' if has_any else '未分层'}")
    analyze_results.append(f"\n结论: {'存在分层' if has_any else '未分层'}")
    layer_result_path=str(Path(data_path).parent)
    with open(layer_result_path+'/精度误差.txt','a',encoding='utf-8') as r:
        r.write('\n\n\n')
        for analyze_result in analyze_results:
            r.write(analyze_result + '\n')
        r.close()




if __name__ == "__main__":
    # if len(sys.argv) < 2:
    #     print("用法: python pointcloud_analyze.py <点云文件路径>")
    #     sys.exit(1)

    #analyze_pointcloud(sys.argv[1])
    #crop_pointscloude(in_path)
    data_path=r"G:\TK-set\2.1data\20260807\b855\2026-08-07_11-42-01"
    crop_pointscloude(data_path)#截取点云
    analyze_pointcloud(data_path)#计算分层

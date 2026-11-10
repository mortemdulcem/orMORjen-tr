# ASO_CBCT/ASO_CBCT_utils/utils.py'den BIREBIR alinan bolumler (satir 123-163, 250-365).
# Kaynak: DCBIA-OrthoLab/SlicerAutomatedDentalTools. Hicbir satir degistirilmedi.
import json
import numpy as np

def LoadJsonLandmarks(ldmk_path, ldmk_list=None):
    """
    Load landmarks from json file

    Parameters
    ----------
    ldmk_path : str
        Path to the json file
    gold : bool, optional
        If True, load gold standard landmarks, by default False

    Returns
    -------
    dict
        Dictionary of landmarks

    Raises
    ------
    ValueError
        If the json file is not valid
    """
    with open(ldmk_path) as f:
        data = json.load(f)

    markups = data["markups"][0]["controlPoints"]

    landmarks = {}
    for markup in markups:
        try:
            lm_ph_coord = np.array(
                [markup["position"][0], markup["position"][1], markup["position"][2]]
            )
            # lm_coord = ((lm_ph_coord - origin) / spacing).astype(np.float16)
            lm_coord = lm_ph_coord.astype(np.float64)
            landmarks[markup["label"]] = lm_coord
        except IndexError:
            continue
    if ldmk_list is not None:
        return {key: landmarks[key] for key in ldmk_list if key in landmarks.keys()}

    return landmarks

def GetDistances(landmark_dic):
    """Compute all distances between all landmarks for a single file"""
    distances = {}

    landmarks = landmark_dic.keys()

    for lm in landmarks:
        distances[lm] = {}
        for lm2 in landmarks:
            if lm != lm2:
                distances[lm][lm2] = np.linalg.norm(
                    landmark_dic[lm] - landmark_dic[lm2]
                )

    return distances


def GetDistDifference(gold_dic, input_dic):
    """Compare the distances between all landmarks for two files in a dictionary"""
    gold = GetDistances(gold_dic)
    test = GetDistances(input_dic)

    differences = {}

    for lm in test.keys():
        differences[lm] = {}
        for lm2 in test[lm].keys():
            differences[lm][lm2] = abs(gold[lm][lm2] - test[lm][lm2])

    return differences


def GetDirections(landmark_dic):
    """Compute all directions between all landmarks for a single file"""
    directions = {}

    landmarks = landmark_dic.keys()

    for lm in landmarks:
        directions[lm] = {}
        for lm2 in landmarks:
            if lm != lm2:
                directions[lm][lm2] = landmark_dic[lm] - landmark_dic[lm2]

    return directions


def GetDirDifference(gold_dic, input_dic):
    """Compare the angular differences between all landmarks for two files in a dictionary"""
    gold = GetDirections(gold_dic)
    test = GetDirections(input_dic)

    angular_diff = {}

    for lm in test.keys():
        angular_diff[lm] = {}
        for lm2 in test[lm].keys():
            angular_diff[lm][lm2] = np.arccos(
                np.dot(gold[lm][lm2], test[lm][lm2])
                / (np.linalg.norm(gold[lm][lm2]) * np.linalg.norm(test[lm][lm2]))
            )

    return angular_diff


def GetCount(differences, max_diff=1, min_diff=0):
    """Count, for each landmark, the number of landmarks that are too far from it"""
    landmark_count = {}

    for lm in differences.keys():
        count = 0
        for lm2 in differences[lm].keys():
            if differences[lm][lm2] > max_diff:
                count += 1
            if differences[lm][lm2] < min_diff:
                count -= 1
        landmark_count[lm] = count

    return landmark_count


def SumCount(distance_count, direction_count):
    """Sum the number count of distance and direction"""
    sum_count = {}

    for lm in distance_count.keys():
        sum_count[lm] = distance_count[lm] + direction_count[lm]

    return sum_count


def GetLandmarkToRemove(input_path, gold_path):
    """Get the list of landmark that should be removed from the landmark dictionary based on the difference with the gold standard"""

    test_ldmk = LoadJsonLandmarks(input_path)
    gold_ldmk = LoadJsonLandmarks(gold_path)

    dist_diff = GetDistDifference(gold_ldmk, test_ldmk)
    dir_diff = GetDirDifference(gold_ldmk, test_ldmk)

    dist_count = GetCount(dist_diff, max_diff=15)
    dir_count = GetCount(dir_diff, max_diff=0.4, min_diff=0.1)

    tot_count = SumCount(dist_count, dir_count)

    removed_landmarks = []
    for lm in tot_count.keys():
        if tot_count[lm] > len(test_ldmk):
            removed_landmarks.append(lm)

    for lm in dir_count.keys():
        if dir_count[lm] > int(len(test_ldmk) / 2):
            if lm not in removed_landmarks:
                removed_landmarks.append(lm)

    return removed_landmarks

"""Descriptive features only; these are not a microplastic classifier."""

WAVELENGTHS_NM = (410, 435, 460, 485, 510, 535, 560, 585, 610, 645, 680, 705, 730, 760, 810, 860, 900, 940)


def describe_spectrum(data: dict) -> dict:
    pairs = [(wave, data.get(f"as7265x_{wave}_nm")) for wave in WAVELENGTHS_NM]
    available = [(wave, float(value)) for wave, value in pairs if value is not None]
    if not available:
        return {"spectrum_channel_count": 0, "spectrum_sum": None,
                "spectrum_peak_nm": None, "spectrum_peak_value": None}
    peak_wave, peak_value = max(available, key=lambda item: item[1])
    return {
        "spectrum_channel_count": len(available),
        "spectrum_sum": sum(value for _, value in available),
        "spectrum_peak_nm": peak_wave,
        "spectrum_peak_value": peak_value,
    }

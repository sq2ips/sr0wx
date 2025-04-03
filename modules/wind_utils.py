def wind_direction_name(angle):
    """Return wind direction name in words based on angle in degrees"""
    angle = angle % 360
    
    if 0 <= angle <= 23:
        return "polnocny"
    elif 23 < angle <= 67:
        return "polnocno wschodni"
    elif 67 < angle <= 112:
        return "wschodni"
    elif 112 < angle <= 157:
        return "poludniowo wschodni"
    elif 157 < angle <= 202:
        return "poludniowy"
    elif 202 < angle <= 247:
        return "poludniowo zachodni"
    elif 247 < angle <= 292:
        return "zachodni"
    elif 292 < angle <= 337:
        return "polnocno zachodni"
    elif 337 < angle <= 360:
        return "polnocny"

if __name__ == "__main__":
    assert wind_direction_name(20) == "polnocny"
    assert wind_direction_name(160) == "poludniowy"
    assert wind_direction_name(260) == "zachodni"
    assert wind_direction_name(400) == "polnocno wschodni"

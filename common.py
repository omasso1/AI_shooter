

class Segment:
    def __init__(self, x1:float, y1:float, x2:float, y2:float):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        #as in form y = ax + b
        if (y2 - y1 == 0):
            y2+=0.000000001
        if (x2 - x1 == 0):
            x2+=0.000000001

        self.a = (y2-y1) / (x2 - x1)
        self.b = y1 - self.a * x1
        
    def value(self, x):
        return self.a * x + self.b
    
    def intersects(self, line2):
        y11 = self.value(line2.x1)
        y12 = self.value(line2.x2)
        y21 = line2.value(self.x1)
        y22 = line2.value(self.x2)
        if (line2.y1 - y11) * (line2.y2 - y12) <= 0 and (self.y1 - y21) * (self.y2 - y22) < 0:
            return True
        return False 
    
def clamp(value, min, max):
    if value > max:
        return max
    if value < min:
        return min
    
    return value


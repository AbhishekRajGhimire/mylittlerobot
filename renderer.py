import math
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen, QPainterPath, QFont
from PyQt6.QtCore import Qt, QPointF

class Renderer:
    @staticmethod
    def draw(pet, painter, cursor_pos):
        cx = pet.width() / 2
        cy = pet.height() / 2
        
        # Hiding offset
        if pet.state == 'hiding':
            nearest_wall_x = 0 if pet.x() < pet.screen_geo.width() / 2 else pet.screen_geo.width() - pet.width()
            if abs(pet.x() - nearest_wall_x) <= 15:
                if pet.x() < pet.screen_geo.width() / 2:
                    cx -= pet.width() * 0.4
                    pet.direction = 1
                else:
                    cx += pet.width() * 0.4
                    pet.direction = -1
        
        flip = False
        if pet.state in ['walking', 'looking_around', 'following', 'hiding']:
            if pet.direction == -1: flip = True
        elif pet.velocity_x < -0.5:
            flip = True
            
        painter.translate(cx, cy + 25)
        if flip:
            painter.scale(-1, 1)
            
        body_color = pet.base_color
        h, s, l, a = body_color.getHsl()
        head_color = QColor.fromHsl(h, s, min(255, l + 30))
        dark_grey = QColor(60, 70, 80)
        yellow_accent = QColor(255, 180, 50)
        
        # JETPACK
        if pet.state == 'flying':
            painter.setBrush(QColor(255, 120, 0)) 
            painter.setPen(Qt.PenStyle.NoPen)
            flicker = math.sin(pet.anim_time * 5) * 10
            
            path = QPainterPath()
            path.moveTo(-15, 20)
            path.lineTo(-5, 20)
            path.lineTo(-10, 40 + flicker)
            painter.drawPath(path)
            
            path = QPainterPath()
            path.moveTo(5, 20)
            path.lineTo(15, 20)
            path.lineTo(10, 40 + flicker)
            painter.drawPath(path)

            painter.setBrush(dark_grey)
            painter.drawRoundedRect(-20, -10, 40, 35, 5, 5)

        # === LIMBS ===
        swing = 0
        head_y = -30
        
        if pet.state in ['walking', 'following', 'dancing']:
            swing = math.sin(pet.anim_time * (4 if pet.state == 'dancing' else 2)) * 12
            head_y -= abs(math.sin(pet.anim_time * (4 if pet.state == 'dancing' else 2))) * 3
            
        is_sitting = pet.state in ['sleeping', 'petting', 'working']
        if is_sitting:
            head_y += 10
            
        head_y = int(head_y)

        # LEGS
        painter.save()
        painter.translate(-12, 25)
        if is_sitting:
            painter.translate(-8, -5)
            painter.rotate(90)
        else:
            painter.rotate(swing * 1.5)
        painter.setPen(QPen(dark_grey, 4))
        painter.drawLine(0, 0, 0, 10)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(body_color)
        painter.drawRoundedRect(-8, 8, 16, 15, 3, 3)
        painter.restore()
        
        painter.save()
        painter.translate(12, 25)
        if is_sitting:
            painter.translate(8, -5)
            painter.rotate(-90)
        else:
            painter.rotate(-swing * 1.5)
        painter.setPen(QPen(dark_grey, 4))
        painter.drawLine(0, 0, 0, 10)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(body_color)
        painter.drawRoundedRect(-8, 8, 16, 15, 3, 3)
        painter.restore()

        # ARMS
        painter.save()
        painter.translate(-25, 0)
        if is_sitting:
            painter.rotate(20)
        else:
            painter.rotate(swing * 2)
        painter.setPen(QPen(dark_grey, 5))
        painter.drawLine(0, 0, 0, 15)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(body_color)
        painter.drawRoundedRect(-6, 12, 12, 12, 3, 3)
        painter.restore()
        
        painter.save()
        painter.translate(25, 0)
        if pet.state in ['waving', 'dancing']:
            wave_angle = -140 + math.sin(pet.anim_time * 8) * 20
            painter.rotate(wave_angle)
        elif is_sitting:
            painter.rotate(-20)
        else:
            painter.rotate(-swing * 2)
        painter.setPen(QPen(dark_grey, 5))
        painter.drawLine(0, 0, 0, 15)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(body_color)
        painter.drawRoundedRect(-6, 12, 12, 12, 3, 3)
        painter.restore()

        # BODY
        painter.setPen(QPen(dark_grey, 3))
        painter.setBrush(body_color)
        painter.drawRoundedRect(-25, -5, 50, 35, 15, 15)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(yellow_accent)
        painter.drawRoundedRect(-15, 20, 30, 8, 3, 3)
        painter.setBrush(QColor(200, 240, 255))
        painter.drawEllipse(QPointF(0, 5), 4, 4)

        # HEAD
        painter.setPen(QPen(dark_grey, 2))
        painter.setBrush(yellow_accent)
        painter.drawRoundedRect(-40, head_y - 10, 10, 20, 2, 2)
        painter.drawRoundedRect(30, head_y - 10, 10, 20, 2, 2)
        
        painter.setPen(QPen(dark_grey, 3))
        painter.drawLine(-15, head_y - 25, -25, head_y - 40)
        painter.drawLine(15, head_y - 25, 25, head_y - 40)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 50, 50)) 
        painter.drawEllipse(QPointF(-27, head_y - 42), 5, 5)
        painter.drawEllipse(QPointF(23, head_y - 42), 5, 5)

        painter.setPen(QPen(dark_grey, 3))
        painter.setBrush(head_color)
        painter.drawRoundedRect(-35, head_y - 25, 70, 50, 15, 15)
        
        if pet.accessory == 'Top Hat':
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(30, 30, 30))
            painter.drawRect(-20, head_y - 50, 40, 25) 
            painter.drawRect(-30, head_y - 25, 60, 5)  
            painter.setBrush(QColor(200, 30, 30))
            painter.drawRect(-20, head_y - 30, 40, 5)  
        elif pet.accessory == 'Bow Tie':
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(220, 30, 30))
            path = QPainterPath()
            path.moveTo(0, head_y + 25)
            path.lineTo(-15, head_y + 15)
            path.lineTo(-15, head_y + 35)
            path.closeSubpath()
            path.moveTo(0, head_y + 25)
            path.lineTo(15, head_y + 15)
            path.lineTo(15, head_y + 35)
            path.closeSubpath()
            painter.drawPath(path)
            painter.setBrush(QColor(180, 20, 20))
            painter.drawEllipse(QPointF(0, head_y + 25), 4, 4)

        # EYES & MOUTH
        if pet.state == 'dizzy':
            painter.setPen(QPen(QColor(30, 50, 100), 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            for i in range(1, 4):
                painter.drawArc(-22, int(head_y) - 8, i*5, i*5, int(pet.anim_time * 50) * 16 % 5760, 2880)
            for i in range(1, 4):
                painter.drawArc(8, int(head_y) - 8, i*5, i*5, int(pet.anim_time * 50) * 16 % 5760, 2880)
            
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(yellow_accent)
            for i in range(3):
                angle = pet.anim_time * 3 + (i * 2.0)
                sx = math.cos(angle) * 45
                sy = head_y - 10 + math.sin(angle) * 15
                painter.drawEllipse(QPointF(sx, sy), 4, 4)
        elif pet.state == 'funny_face':
            # Cute anime wincing eyes (> <)
            painter.setPen(QPen(dark_grey, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            
            # Left eye: >
            path = QPainterPath()
            path.moveTo(-22, head_y - 12)
            path.lineTo(-12, head_y - 6)
            path.lineTo(-22, head_y)
            painter.drawPath(path)
            
            # Right eye: <
            path = QPainterPath()
            path.moveTo(22, head_y - 12)
            path.lineTo(12, head_y - 6)
            path.lineTo(22, head_y)
            painter.drawPath(path)
            
            # Tiny little "ouch" mouth
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(200, 100, 100)) # reddish
            painter.drawEllipse(QPointF(0, head_y + 10), 3, 4)
            
            # Cute blush patches
            painter.setBrush(QColor(255, 150, 150, 150))
            painter.drawEllipse(QPointF(-25, head_y + 5), 6, 4)
            painter.drawEllipse(QPointF(25, head_y + 5), 6, 4)
        elif pet.state == 'petting':
            # Heart Eyes <3
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(255, 50, 100))
            for offset in [-16, 16]:
                path = QPainterPath()
                # Draw small heart manually using bezier or arcs
                path.moveTo(offset, head_y + 4)
                path.arcTo(offset - 6, head_y - 8, 6, 6, 0, 180)
                path.arcTo(offset, head_y - 8, 6, 6, 0, 180)
                painter.drawPath(path) # Close enough to a heart shape for now, let's refine
                
                # Better heart:
                path2 = QPainterPath()
                path2.moveTo(offset, head_y - 2)
                path2.cubicTo(offset - 10, head_y - 10, offset - 10, head_y, offset, head_y + 8)
                path2.cubicTo(offset + 10, head_y, offset + 10, head_y - 10, offset, head_y - 2)
                painter.drawPath(path2)
            
            # Tiny smile
            painter.setPen(QPen(dark_grey, 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawArc(-5, int(head_y) + 10, 10, 6, -30 * 16, -120 * 16)
        elif pet.state == 'sleeping':
            painter.setPen(QPen(QColor(30, 50, 100), 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawArc(-20, int(head_y) - 2, 12, 12, -30 * 16, -120 * 16)
            painter.drawArc(8, int(head_y) - 2, 12, 12, -30 * 16, -120 * 16)
            
            painter.setPen(QPen(dark_grey, 2))
            painter.drawArc(-5, int(head_y) + 12, 10, 6, -30 * 16, -120 * 16)
            
            painter.setFont(QFont("Comic Sans MS", 10, QFont.Weight.Bold))
            for z in pet.zzz_particles:
                alpha = max(0, 255 - int((z['age'] / 100.0) * 255))
                painter.setPen(QPen(QColor(100, 150, 255, alpha)))
                painter.drawText(QPointF(z['x'], z['y'] + head_y), "Zzz")
        else:
            global_center_x = pet.x() + cx
            global_center_y = pet.y() + cy + head_y
            actual_cursor_x = cursor_pos.x()
            if flip: actual_cursor_x = global_center_x - (cursor_pos.x() - global_center_x)
            
            dx = actual_cursor_x - global_center_x
            dy = cursor_pos.y() - global_center_y
            dist = math.hypot(dx, dy)
            if dist > 0: dx /= dist; dy /= dist
                
            eye_shift_x = dx * 3
            eye_shift_y = dy * 2

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(40, 80, 130))
            painter.drawRoundedRect(int(-22 + eye_shift_x), int(head_y - 12 + eye_shift_y), 16, 24, 6, 6)
            painter.drawRoundedRect(int(6 + eye_shift_x), int(head_y - 12 + eye_shift_y), 16, 24, 6, 6)
            
            painter.setBrush(QColor(255, 255, 255))
            painter.drawEllipse(QPointF(-16 + eye_shift_x, head_y - 6 + eye_shift_y), 4, 5)
            painter.drawEllipse(QPointF(12 + eye_shift_x, head_y - 6 + eye_shift_y), 4, 5)
            
            painter.drawEllipse(QPointF(-12 + eye_shift_x, head_y + 4 + eye_shift_y), 2, 2)
            painter.drawEllipse(QPointF(16 + eye_shift_x, head_y + 4 + eye_shift_y), 2, 2)

            painter.setPen(QPen(dark_grey, 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawArc(-5, int(head_y) + 12, 10, 6, -30 * 16, -120 * 16)

            if math.sin(pet.anim_time * 0.5) > 0.95:
                painter.setBrush(head_color)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRect(-25, int(head_y) - 15, 50, 30)
                painter.setPen(QPen(dark_grey, 2))
                painter.drawLine(-22, int(head_y), -6, int(head_y))
                painter.drawLine(6, int(head_y), 22, int(head_y))
                
        # Working state (draws over face)
        if pet.state == 'working':
            # Reading glasses
            painter.setPen(QPen(dark_grey, 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(-24, int(head_y) - 14, 20, 28, 4, 4)
            painter.drawRoundedRect(4, int(head_y) - 14, 20, 28, 4, 4)
            painter.drawLine(-4, int(head_y), 4, int(head_y))

        if pet.accessory == 'Sunglasses':
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(20, 20, 20))
            painter.drawRoundedRect(-25, int(head_y) - 12, 20, 16, 4, 4)
            painter.drawRoundedRect(5, int(head_y) - 12, 20, 16, 4, 4)
            painter.setPen(QPen(QColor(20, 20, 20), 3))
            painter.drawLine(-5, int(head_y) - 8, 5, int(head_y) - 8)

        # Working state laptop (draws over body)
        if pet.state == 'working':
            # Screen
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(180, 180, 190))
            painter.drawRect(-20, 10, 40, 25)
            # Glowing screen overlay
            painter.setBrush(QColor(150, 220, 255, 150))
            painter.drawRect(-18, 12, 36, 21)
            # Base
            painter.setBrush(QColor(150, 150, 160))
            path = QPainterPath()
            path.moveTo(-25, 35)
            path.lineTo(25, 35)
            path.lineTo(35, 42)
            path.lineTo(-35, 42)
            painter.drawPath(path)
            # Tiny glowing apple logo
            painter.setBrush(QColor(255, 255, 255))
            painter.drawEllipse(QPointF(0, 22), 3, 3)

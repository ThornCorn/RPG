import random as r
#овощ

def ask(n):
    while True:
        s = input("> ").strip()
        if s.isdigit() and 1 <= int(s) <= n:
            return int(s)
        print("Неверный ввод")


class hero:
    tl = "Герой"

    def __init__(self, name, hp, pwr, spd, arm, mag, ag, mp=30):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.pwr = pwr
        self.spd = spd
        self.arm = arm
        self.mag = mag
        self.ag = ag
        self.mp = mp
        self.max_mp = mp

        self.lvl = 1
        self.exp = 0
        self.is_alive = True
        self.und = False
        self.fx = {}
        self.pot = 2
        self.pf = 0.35

    def get_stats(self):
        return {
            'name': self.name,
            'cls': self.tl,
            'hp': f"{self.hp}/{self.max_hp}",
            'mp': f"{self.mp}/{self.max_mp}",
            'pwr': self.pwr,
            'spd': self.spd,
            'arm': self.arm,
            'mag': self.mag,
            'ag': self.ag,
            'exp': f"{self.exp}/{self.lvl * 50}",
            'pot': self.pot,
            'level': self.lvl
        }

    def show_stats(self):
        s = self.get_stats()
        print(f"=== {s['name']} [{s['cls']}] (lvl {s['level']}) ===")
        for k, v in s.items():
            if k not in ('name', 'cls', 'level'):
                print(f"{k}: {v}")

    def fv(self, k):
        return self.fx[k][1] if k in self.fx else 0

    def atk(self):
        return max(1, self.pwr + self.fv('ярость') - self.fv('слабость'))

    def dfn(self):
        return max(0, self.arm + self.fv('щит') - self.fv('кислота'))

    def die(self):
        self.is_alive = False
        print(f"{self.name} помер")

    def take_damage(self, d, mg=False):
        if not self.is_alive:
            return 0
        if r.random() < (self.ag + self.fv('уклон')) / 200:
            print(f"{self.name} уклоняется")
            return 0
        a = self.dfn() // 2 if mg else self.dfn()
        d = max(1, round(d - a))
        self.hp -= d
        print(f"{self.name} получает {d} урона [{max(0, self.hp)}/{self.max_hp}]")
        if self.hp <= 0:
            self.die()
        return d

    def heal(self, n):
        n = min(self.max_hp - self.hp, round(n))
        if n > 0:
            self.hp += n
            print(f"{self.name} восстановил {n} HP")
        return n

    def hit(self, t, d, mg=False, cr=0):
        if r.random() < self.ag / 100 + cr:
            d *= 1.5
            print("Критический удар!")
        return t.take_damage(d, mg)

    def basic_attack(self, t):
        print(f"{self.name} атакует {t.name}")
        return self.hit(t, self.atk())

    def acts(self):
        return [("Атака", 0, self.basic_attack)]

    def use(self, a, t):
        n, c, f = a
        if self.mp < c:
            print("Недостаточно маны")
            return False
        self.mp -= c
        f(t)
        return True

    def drink(self):
        if not self.pot:
            print("Зелий нет")
            return False
        self.pot -= 1
        print(f"{self.name} пьёт зелье")
        self.heal(self.max_hp * self.pf)
        return True

    def tick(self):
        st = 'стан' in self.fx
        for k in list(self.fx):
            n, v = self.fx[k]
            if k in ('яд', 'огонь'):
                self.hp -= v
                print(f"{self.name}: {k} наносит {v} урона [{max(0, self.hp)}/{self.max_hp}]")
            elif k == 'реген':
                self.heal(v)
            if n <= 1:
                del self.fx[k]
            else:
                self.fx[k] = [n - 1, v]
        if self.hp <= 0:
            self.die()
            return False
        self.mp = min(self.max_mp, self.mp + 3)
        if st:
            print(f"{self.name} оглушён и пропускает ход")
        return not st

    def after(self, t):
        pass

    def rest(self):
        self.fx.clear()
        self.heal(self.max_hp * 0.5)
        self.mp = self.max_mp

    def gain_exp(self, n):
        self.exp += n
        print(f"{self.name} получает {n} опыта")
        while self.exp >= self.lvl * 50:
            self.exp -= self.lvl * 50
            self.lvl += 1
            self.max_hp += 10
            self.max_mp += 5
            self.pwr += 2
            self.arm += 1
            self.mag += 2
            self.ag += 1
            self.spd += 1
            self.hp = self.max_hp
            self.mp = self.max_mp
            print(f"*** {self.name} достиг {self.lvl} уровня! ***")


class monk(hero):
    tl = "Монах"

    def __init__(self, name):
        super().__init__(name, 70, 11, 13, 5, 8, 14)
        self.kata = ["Горы", "Небес", "Штиль", "Бури"]
        self.kt = None

    def get_stats(self):
        s = super().get_stats()
        s['kata'] = self.kt or "-"
        return s

    def acts(self):
        return super().acts() + [
            ("Смена стойки", 0, self.kata_change),
            ("Удар ладони", 10, self.palm)
        ]

    def atk(self):
        return super().atk() * (1.3 if self.kt == "Бури" else 1)

    def dfn(self):
        return super().dfn() * (1.3 if self.kt == "Горы" else 1)

    def kata_change(self, t=None):
        for i, k in enumerate(self.kata, 1):
            print(f"{i}. {k}")
        self.kt = self.kata[ask(4) - 1]
        print(f"{self.name} принимает стойку {self.kt}")

    def palm(self, t):
        print(f"{self.name} бьёт открытой ладонью")
        if self.hit(t, self.atk() + self.mag) and r.random() < 0.3:
            t.fx['стан'] = [1, 0]
            print(f"{t.name} оглушён")

    def take_damage(self, d, mg=False):
        if self.is_alive and self.kt == "Небес" and r.random() < 0.2:
            print(f"{self.name} уходит от удара")
            return 0
        return super().take_damage(d, mg)

    def tick(self):
        if self.kt == "Штиль":
            self.heal(3)
        return super().tick()


class alchemist(hero):
    tl = "Алхимик"

    def __init__(self, name):
        super().__init__(name, 70, 9, 11, 5, 14, 12, 40)
        self.pot = 4
        self.pf = 0.5

    def acts(self):
        return super().acts() + [
            ("Кислота", 8, self.acid),
            ("Взрывная колба", 14, self.bomb),
            ("Эликсир силы", 10, self.elix)
        ]

    def acid(self, t):
        print(f"{self.name} плещет кислотой")
        if self.hit(t, self.mag, True):
            t.fx['кислота'] = [3, 3]

    def bomb(self, t):
        print(f"{self.name} бросает взрывную колбу")
        if self.hit(t, self.mag * 1.8, True):
            t.fx['огонь'] = [2, self.mag // 3]

    def elix(self, t):
        print(f"{self.name} выпивает эликсир силы")
        self.heal(self.mag)
        self.fx['ярость'] = [3, 5]


class paladin(hero):
    tl = "Паладин"

    def __init__(self, name):
        super().__init__(name, 95, 12, 8, 8, 9, 6)

    def acts(self):
        return super().acts() + [
            ("Священный удар", 10, self.smite),
            ("Божественный щит", 12, self.shield),
            ("Возложение рук", 15, self.lay)
        ]

    def smite(self, t):
        print(f"{self.name} наносит священный удар")
        d = self.atk() + self.mag
        if t.und:
            d *= 1.5
            print("Свет жжёт нежить!")
        self.hit(t, d, True)

    def shield(self, t):
        print(f"{self.name} окружает себя божественным щитом")
        self.fx['щит'] = [3, 6]

    def lay(self, t):
        print(f"{self.name} возлагает руки")
        self.heal(self.mag * 3)


class warlock(hero):
    tl = "Колдун"

    def __init__(self, name):
        super().__init__(name, 70, 8, 10, 5, 16, 10, 45)

    def acts(self):
        return super().acts() + [
            ("Мистический заряд", 6, self.bolt),
            ("Проклятие", 10, self.curse),
            ("Похищение жизни", 16, self.leech),
            ("Кровавый пакт", 0, self.pact)
        ]

    def bolt(self, t):
        print(f"{self.name} выпускает мистический заряд")
        self.hit(t, self.mag * 1.5, True)

    def curse(self, t):
        print(f"{self.name} проклинает {t.name}")
        t.fx['слабость'] = [3, 5]
        t.fx['яд'] = [3, self.mag // 3]

    def leech(self, t):
        print(f"{self.name} похищает жизнь")
        self.heal(self.hit(t, self.mag * 1.6, True) // 2)

    def pact(self, t):
        c = self.max_hp // 6
        if self.hp <= c:
            print("Слишком мало здоровья для пакта")
            return
        self.hp -= c
        self.mp = min(self.max_mp, self.mp + 20)
        print(f"{self.name} жертвует {c} HP и получает 20 MP")


class rogue(hero):
    tl = "Плут"

    def __init__(self, name):
        super().__init__(name, 70, 15, 16, 5, 4, 20)

    def acts(self):
        return super().acts() + [
            ("Удар в спину", 10, self.back),
            ("Ядовитый клинок", 8, self.pois),
            ("Дымовая шашка", 10, self.smoke)
        ]

    def back(self, t):
        print(f"{self.name} заходит со спины")
        self.hit(t, self.atk() * 1.6, cr=0.4)

    def pois(self, t):
        print(f"{self.name} бьёт отравленным клинком")
        if self.hit(t, self.atk()):
            t.fx['яд'] = [4, 5]

    def smoke(self, t):
        print(f"{self.name} скрывается в дыму")
        self.fx['уклон'] = [2, 80]


class necromancer(hero):
    tl = "Некромант"

    def __init__(self, name):
        super().__init__(name, 70, 7, 9, 5, 15, 8, 45)
        self.pet = 0

    def acts(self):
        return super().acts() + [
            ("Поднять скелета", 15, self.summon),
            ("Костяное копьё", 8, self.spear),
            ("Вытягивание жизни", 12, self.drain)
        ]

    def summon(self, t):
        self.pet = 5
        print(f"{self.name} поднимает скелета")

    def spear(self, t):
        print(f"{self.name} метает костяное копьё")
        self.hit(t, self.mag * 1.6, True)

    def drain(self, t):
        print(f"{self.name} вытягивает жизнь из {t.name}")
        self.heal(self.hit(t, self.mag * 1.2, True))

    def after(self, t):
        if self.pet and t.is_alive:
            print("Скелет атакует")
            t.take_damage(self.mag)
            self.pet -= 1
            if not self.pet:
                print("Скелет рассыпается")

    def rest(self):
        super().rest()
        self.pet = 0


class warrior(hero):
    tl = "Воин"

    def __init__(self, name):
        super().__init__(name, 100, 14, 9, 7, 2, 8, 25)
        self.sw = True

    def acts(self):
        return super().acts() + [
            ("Мощный удар", 8, self.smash),
            ("Боевой клич", 10, self.cry),
            ("Глухая оборона", 6, self.guard)
        ]

    def smash(self, t):
        print(f"{self.name} наносит мощный удар")
        self.hit(t, self.atk() * 1.8)

    def cry(self, t):
        print(f"{self.name} издаёт боевой клич")
        self.fx['ярость'] = [3, 6]

    def guard(self, t):
        print(f"{self.name} уходит в глухую оборону")
        self.fx['щит'] = [2, 10]

    def tick(self):
        if self.sw and 0 < self.hp < self.max_hp * 0.3:
            self.sw = False
            print(f"{self.name} открывает второе дыхание")
            self.heal(self.max_hp * 0.25)
        return super().tick()

    def rest(self):
        super().rest()
        self.sw = True


class priest(hero):
    tl = "Жрец"

    def __init__(self, name):
        super().__init__(name, 80, 8, 9, 6, 14, 7, 50)

    def acts(self):
        return super().acts() + [
            ("Святой свет", 8, self.light),
            ("Исцеление", 12, self.cure),
            ("Обновление", 10, self.renew),
            ("Очищение", 6, self.purge)
        ]

    def light(self, t):
        print(f"{self.name} обрушивает святой свет")
        d = self.mag * 1.5
        if t.und:
            d *= 2
            print("Нежить корчится от света!")
        self.hit(t, d, True)

    def cure(self, t):
        print(f"{self.name} читает молитву исцеления")
        self.heal(self.mag * 3)

    def renew(self, t):
        print(f"{self.name} накладывает обновление")
        self.fx['реген'] = [4, self.mag // 2]

    def purge(self, t):
        print(f"{self.name} очищается от скверны")
        for k in ('яд', 'огонь', 'слабость', 'кислота', 'стан'):
            self.fx.pop(k, None)
        self.heal(10)


class ranger(hero):
    tl = "Следопыт"

    def __init__(self, name):
        super().__init__(name, 80, 14, 13, 5, 6, 16)

    def acts(self):
        return super().acts() + [
            ("Прицельный выстрел", 8, self.aim),
            ("Залп", 12, self.volley),
            ("Капкан", 10, self.trap)
        ]

    def aim(self, t):
        print(f"{self.name} делает прицельный выстрел")
        self.hit(t, self.atk() * 1.5, cr=0.25)

    def volley(self, t):
        print(f"{self.name} выпускает залп стрел")
        for _ in range(3):
            self.hit(t, self.atk() * 0.7)

    def trap(self, t):
        print(f"{self.name} ставит капкан")
        if self.hit(t, self.atk() * 0.5):
            t.fx['стан'] = [1, 0]
            print(f"{t.name} попал в капкан")


class barbarian(hero):
    tl = "Варвар"

    def __init__(self, name):
        super().__init__(name, 120, 16, 10, 5, 2, 6, 20)

    def acts(self):
        return super().acts() + [
            ("Ярость", 0, self.rage),
            ("Безрассудный удар", 5, self.reck),
            ("Устрашающий рёв", 8, self.roar)
        ]

    def atk(self):
        return super().atk() * (1.4 if self.hp < self.max_hp / 2 else 1)

    def rage(self, t):
        print(f"{self.name} впадает в ярость, забыв о защите")
        self.fx['ярость'] = [3, 8]
        self.fx['кислота'] = [3, 2]

    def reck(self, t):
        print(f"{self.name} бьёт не глядя")
        c = round(self.hit(t, self.atk() * 2.2) * 0.2)
        if c:
            self.hp -= c
            print(f"{self.name} получает {c} урона отдачей [{max(0, self.hp)}/{self.max_hp}]")
            if self.hp <= 0:
                self.die()

    def roar(self, t):
        print(f"{self.name} ревёт, {t.name} теряет решимость")
        t.fx['слабость'] = [3, 5]


class bard(hero):
    tl = "Бард"

    def __init__(self, name):
        super().__init__(name, 85, 10, 12, 6, 14, 13, 40)

    def acts(self):
        return super().acts() + [
            ("Диссонанс", 8, self.dis),
            ("Вдохновение", 10, self.insp),
            ("Колыбельная", 14, self.lull),
            ("Песнь исцеления", 10, self.song)
        ]

    def dis(self, t):
        print(f"{self.name} играет режущий уши аккорд")
        if self.hit(t, self.mag * 1.6, True) and r.random() < 0.25:
            t.fx['стан'] = [1, 0]
            print(f"{t.name} оглушён")

    def insp(self, t):
        print(f"{self.name} вдохновляет себя балладой")
        self.fx['ярость'] = [3, 6]
        self.fx['уклон'] = [3, 40]

    def lull(self, t):
        print(f"{self.name} поёт колыбельную")
        self.hit(t, self.mag * 0.8, True)
        if t.is_alive and r.random() < 0.6:
            t.fx['стан'] = [2, 0]
            print(f"{t.name} засыпает")
        else:
            print(f"{t.name} сопротивляется")

    def song(self, t):
        print(f"{self.name} исполняет песнь исцеления")
        self.fx['реген'] = [3, self.mag // 2 + 2]


class enemy(hero):
    def __init__(self, name, hp, pwr, spd, arm, mag, ag, xp, und=False, sk=None):
        super().__init__(name, hp, pwr, spd, arm, mag, ag)
        self.xp = xp
        self.und = und
        self.sk = sk

    def ai(self, t):
        if self.sk and r.random() < 0.3:
            self.sk(self, t)
        else:
            self.basic_attack(t)


def s_yad(s, t):
    print(f"{s.name} кусает ядовитыми жвалами")
    if s.hit(t, s.atk()):
        t.fx['яд'] = [3, s.mag]


def s_howl(s, t):
    print(f"{s.name} воет и приходит в ярость")
    s.fx['ярость'] = [3, 4]


def s_stun(s, t):
    print(f"{s.name} бьёт дубиной по голове")
    if s.hit(t, s.atk()) and r.random() < 0.4:
        t.fx['стан'] = [1, 0]
        print(f"{t.name} оглушён")


def s_drain(s, t):
    print(f"{s.name} пьёт кровь")
    s.heal(s.hit(t, s.mag * 1.5, True))


def s_regen(s, t):
    print(f"{s.name} затягивает раны")
    s.fx['реген'] = [3, 8]


def s_fire(s, t):
    print(f"{s.name} извергает пламя")
    if s.hit(t, s.mag * 2, True):
        t.fx['огонь'] = [2, s.mag // 2]


MOBS = [
    ("Гоблин", 40, 12, 12, 1, 2, 10, 20, False, None),
    ("Волк", 45, 13, 15, 1, 3, 15, 22, False, s_howl),
    ("Скелет", 50, 13, 8, 4, 2, 5, 25, True, None),
    ("Паук", 40, 12, 14, 2, 5, 14, 25, False, s_yad),
    ("Орк", 70, 15, 8, 4, 2, 6, 35, False, s_stun),
    ("Вампир", 60, 14, 12, 3, 8, 12, 40, True, s_drain),
    ("Тролль", 90, 16, 6, 5, 2, 4, 45, False, s_regen),
]

BOSS = ("Дракон", 200, 18, 10, 5, 10, 8, 200, False, s_fire)

CLS = [monk, alchemist, paladin, warlock, rogue, necromancer,
       warrior, priest, ranger, barbarian, bard]

N = 7


def mob(w):
    n, hp, p, s, a, mg, ag, xp, u, sk = r.choice(MOBS[:min(len(MOBS), w + 2)])
    k = 1 + 0.1 * (w - 1)
    return enemy(n, round(hp * k), round(p * k), s, a + (w - 1) // 3,
                 round(mg * k), ag, round(xp * k), u, sk)


def pick():
    print("Выбери класс:")
    for i, c in enumerate(CLS, 1):
        print(f"{i}. {c.tl}")
    c = CLS[ask(len(CLS)) - 1]
    n = input("Имя героя: ").strip() or c.tl
    return c(n)


def fxs(u):
    return ", ".join(f"{k}({v[0]})" for k, v in u.fx.items()) or "-"


def turn(h, e):
    while True:
        a = h.acts()
        print(f"\n{h.name}: HP {h.hp}/{h.max_hp} MP {h.mp}/{h.max_mp} | эффекты: {fxs(h)}")
        print(f"{e.name}: HP {e.hp}/{e.max_hp} | эффекты: {fxs(e)}")
        for i, (n, c, _) in enumerate(a, 1):
            print(f"{i}. {n}" + (f" [{c} MP]" if c else ""))
        print(f"{len(a) + 1}. Зелье [{h.pot}]")
        print(f"{len(a) + 2}. Характеристики")
        k = ask(len(a) + 2)
        if k == len(a) + 2:
            h.show_stats()
            continue
        if k == len(a) + 1:
            if h.drink():
                return
            continue
        if h.use(a[k - 1], e):
            return


def fight(h, e):
    print(f"\n*** Появляется {e.name}! HP {e.hp} ***")
    rd = 1
    while h.is_alive and e.is_alive:
        print(f"\n--- Раунд {rd} ---")
        for u in sorted((h, e), key=lambda x: x.spd + r.random() * 5, reverse=True):
            if not (h.is_alive and e.is_alive):
                break
            if not u.tick():
                continue
            if u is h:
                turn(h, e)
                h.after(e)
            else:
                e.ai(h)
        rd += 1
    return h.is_alive


def main():
    print("=== ПОДЗЕМЕЛЬЕ ===")
    h = pick()
    h.show_stats()
    for w in range(1, N + 1):
        print(f"\n========== Волна {w}/{N} ==========")
        e = enemy(*BOSS) if w == N else mob(w)
        if not fight(h, e):
            print(f"\nИгра окончена. {h.name} пал на волне {w}")
            return
        print(f"\n{e.name} повержен!")
        h.gain_exp(e.xp)
        if w < N:
            h.rest()
            if r.random() < 0.4:
                h.pot += 1
                print("Найдено зелье лечения")
            while True:
                print("1. Дальше\n2. Характеристики")
                if ask(2) == 1:
                    break
                h.show_stats()
    print(f"\nПОБЕДА! {h.name} одолел дракона")
    h.show_stats()


if __name__ == "__main__":
    main()

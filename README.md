# Snek Volt

An electromagnetic circuit snake game written in Python with Pygame (`pygame-ce`), featuring custom magnetic polarity mechanics, overclock dash traces, phase relay portals, and EMP surge rings.

![Snek Volt Gameplay](snek_volt_gameplay.png)

## Custom Gameplay Mechanics

1. **Magnetic Polarity Reversal (`SPACE`)** Switch the snake between Positive (`+`, Cyan) and Negative (`-`, Amber) charge at any time. Capacitor Orbs with the opposite polarity magnetically attract toward the snake head within a 3-tile radius and award `2x` voltage score.
2. **Overclock Dash & Conductive Traces (`SHIFT`)** Burn stored capacitor energy (`0-100%`) to sprint at `2x` grid speed while laying down conductive green copper traces across the circuit board.
3. **Phase Relay Portals** Paired purple and magenta circuit vias teleport the snake across the board while preserving momentum and active charge polarity.
4. **EMP Surge Waves** Expanding electromagnetic ring hazards spawn when inductors overload; match their polarity to absorb them for `+20` bonus points or dodge them to protect your tail segments.

## Controls

- `WASD` or `Arrow Keys` Steer snake head
- `SPACE` Invert magnetic charge polarity (`+` / `-`)
- `LEFT SHIFT` / `RIGHT SHIFT` Hold for Overclock Dash (`2x` speed)
- `R` Reboot circuit after a fault

## Run from Source

```bash
pip install -r requirements.txt
python main.py
```

## Standalone Executables & Releases

Prebuilt standalone executables (`snek-volt-win64.exe`, `snek-volt-macos`, `snek-volt-linux`) are published on the [GitHub Releases](https://github.com/draarivpatel-ui/snek-volt/releases/tag/v1.0.0) page, and an interactive browser build is live at `https://aariv.me/snek-volt/`.

"""
Playwright script (Python) — PokemonDB Pokemon Info
Look up Pokemon information from PokemonDB.
"""

import os, sys, shutil
from dataclasses import dataclass, field
from typing import List
from playwright.sync_api import sync_playwright, Page

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cdp_utils import get_free_port, get_temp_profile_dir, launch_chrome, wait_for_cdp_ws
from playwright_debugger import checkpoint


@dataclass(frozen=True)
class PokemonRequest:
    pokemon: str = "pikachu"


@dataclass
class PokemonInfo:
    name: str = ""
    pokedex_number: str = ""
    types: str = ""
    abilities: str = ""
    hp: str = ""
    attack: str = ""
    defense: str = ""
    sp_atk: str = ""
    sp_def: str = ""
    speed: str = ""
    evolution_chain: str = ""


@dataclass
class PokemonResult:
    info: PokemonInfo = None

    def __post_init__(self):
        if self.info is None:
            self.info = PokemonInfo()


# Looks up a Pokemon on PokemonDB and extracts name, Pokedex number,
# types, abilities, base stats, and evolution chain.
def get_pokemon_info(page: Page, request: PokemonRequest) -> PokemonResult:
    url = f"https://pokemondb.net/pokedex/{request.pokemon}"
    print(f"Loading {url}...")
    checkpoint("Navigate to PokemonDB")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(3000)

    result = PokemonResult()

    checkpoint("Extract Pokemon info")
    js_code = """() => {
        const info = { name: '', pokedex_number: '', types: '', abilities: '',
                       hp: '', attack: '', defense: '', sp_atk: '', sp_def: '', speed: '',
                       evolution_chain: '' };
        const body = document.body.innerText;
        const lines = body.split('\\n').map(l => l.trim()).filter(l => l.length > 0);

        // Name from h1
        const nameEl = document.querySelector('h1');
        info.name = nameEl ? nameEl.textContent.trim() : '';

        // Find Pokedex data section
        let typesFound = false;
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            if (/^National/.test(line)) {
                const m = line.match(/(\\d{4})/);
                if (m) info.pokedex_number = m[1];
            }
            if (!typesFound && /^Type\\s/.test(line)) {
                const typeStr = line.replace(/^Type\\s+/, '');
                // Only accept if it looks like type names (ELECTRIC, FIRE, etc.)
                if (/^[A-Z]/.test(typeStr) && !/Generation/i.test(typeStr)) {
                    info.types = typeStr;
                    typesFound = true;
                }
            }
            if (/^Abilities/.test(line)) {
                // Abilities line: "Abilities   1. Static"
                const abilStr = line.replace(/^Abilities\\s+/, '');
                const parts = [abilStr];
                // Next line might be hidden ability
                if (i + 1 < lines.length && /hidden ability/i.test(lines[i + 1])) {
                    parts.push(lines[i + 1]);
                }
                info.abilities = parts.join(', ').replace(/\\d+\\.\\s*/g, '');
            }
        }

        // Base stats - lines like "HP  35" then "180 274" (min/max)
        const statMap = { 'HP': 'hp', 'Attack': 'attack', 'Defense': 'defense',
                          'Sp. Atk': 'sp_atk', 'Sp. Def': 'sp_def', 'Speed': 'speed' };
        for (let i = 0; i < lines.length; i++) {
            for (const [label, key] of Object.entries(statMap)) {
                const re = new RegExp('^' + label.replace('.', '\\\\.') + '\\\\s+(\\\\d+)');
                const m = lines[i].match(re);
                if (m) { info[key] = m[1]; break; }
            }
        }

        // Evolution chain
        const evoDiv = document.querySelector('.infocard-list-evo');
        if (evoDiv) {
            const names = evoDiv.querySelectorAll('.ent-name');
            const seen = new Set();
            const chain = [];
            for (const n of names) {
                const nm = n.textContent.trim();
                if (!seen.has(nm)) { seen.add(nm); chain.push(nm); }
            }
            info.evolution_chain = chain.join(' \\u2192 ');
        }

        return info;
    }"""
    data = page.evaluate(js_code)

    result.info.name = data.get("name", "")
    result.info.pokedex_number = data.get("pokedex_number", "")
    result.info.types = data.get("types", "")
    result.info.abilities = data.get("abilities", "")
    result.info.hp = data.get("hp", "")
    result.info.attack = data.get("attack", "")
    result.info.defense = data.get("defense", "")
    result.info.sp_atk = data.get("sp_atk", "")
    result.info.sp_def = data.get("sp_def", "")
    result.info.speed = data.get("speed", "")
    result.info.evolution_chain = data.get("evolution_chain", "")

    print(f"\n  {result.info.name} #{result.info.pokedex_number}")
    print(f"  Types: {result.info.types}")
    print(f"  Abilities: {result.info.abilities}")
    print(f"  Stats: HP={result.info.hp} Atk={result.info.attack} Def={result.info.defense} SpAtk={result.info.sp_atk} SpDef={result.info.sp_def} Spd={result.info.speed}")
    print(f"  Evolution: {result.info.evolution_chain}")

    return result


def test_func():
    port = get_free_port()
    profile_dir = get_temp_profile_dir("pokemondb")
    chrome_proc = launch_chrome(profile_dir, port)
    ws_url = wait_for_cdp_ws(port)

    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp(ws_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        try:
            result = get_pokemon_info(page, PokemonRequest())
            print("\n=== DONE ===")
        finally:
            browser.close()
            chrome_proc.terminate()
            shutil.rmtree(profile_dir, ignore_errors=True)


if __name__ == "__main__":
    from playwright_debugger import run_with_debugger
    run_with_debugger(test_func)

"""Parser and command table for Hermes Tavern `/rp` gateway commands."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RPCommand:
    name: str
    args: list[str]
    raw: str


@dataclass(frozen=True)
class TavernCommandEntry:
    """A single entry in the Tavern command dispatch table.

    handler: method name on TavernRuntime.
    needs_command / needs_event: control which args are passed to the handler.
    help_lines: one or more usage lines shown by /rp help.
    """

    handler: str
    help_lines: list[str] = field(default_factory=list)
    needs_command: bool = True
    needs_event: bool = True


# Top-level /rp command dispatch table.
# Maps command name → TavernCommandEntry.  Order matters for /rp help ordering.
TAVERN_COMMAND_TABLE: dict[str, TavernCommandEntry] = {
    "help": TavernCommandEntry(
        handler="",
        help_lines=["/rp help"],
        needs_command=False,
        needs_event=False,
    ),
    "status": TavernCommandEntry(
        handler="_status",
        help_lines=["/rp status"],
        needs_command=False,
    ),
    "doctor": TavernCommandEntry(
        handler="_doctor",
        help_lines=["/rp doctor"],
        needs_command=False,
    ),
    "start": TavernCommandEntry(
        handler="_start",
        help_lines=["/rp start <card>"],
    ),
    "end": TavernCommandEntry(
        handler="_end",
        help_lines=["/rp end"],
        needs_command=False,
    ),
    "pause": TavernCommandEntry(
        handler="_pause",
        help_lines=["/rp pause"],
        needs_command=False,
    ),
    "resume": TavernCommandEntry(
        handler="_resume",
        help_lines=["/rp resume"],
        needs_command=False,
    ),
    # ── turn controls ──
    "say": TavernCommandEntry(
        handler="_say",
        help_lines=["/rp say <message>"],
    ),
    "greeting": TavernCommandEntry(
        handler="_greeting",
        help_lines=["/rp greeting list", "/rp greeting use <0..N>"],
    ),
    "retry": TavernCommandEntry(
        handler="_retry",
        help_lines=["/rp retry"],
        needs_command=False,
    ),
    "speak": TavernCommandEntry(
        handler="_speak",
        help_lines=["/rp speak"],
        needs_command=False,
    ),
    "voice": TavernCommandEntry(
        handler="_voice",
        help_lines=["/rp voice [on|off]"],
    ),
    "swipe": TavernCommandEntry(
        handler="_swipe",
        help_lines=["/rp swipe list", "/rp swipe add", "/rp swipe use <n>"],
    ),
    "undo": TavernCommandEntry(
        handler="_undo",
        help_lines=["/rp undo"],
        needs_command=False,
    ),
    "edit": TavernCommandEntry(
        handler="_edit",
        help_lines=["/rp edit last <text>"],
    ),
    "history": TavernCommandEntry(
        handler="_history",
        help_lines=["/rp history [limit] [page]"],
    ),
    # ── session management ──
    "session": TavernCommandEntry(
        handler="_session_command",
        help_lines=["/rp session info"],
    ),
    "sessions": TavernCommandEntry(
        handler="_sessions",
        help_lines=["/rp sessions [all] [limit] [page]"],
    ),
    "switch": TavernCommandEntry(
        handler="_switch",
        help_lines=["/rp switch <session-id>"],
    ),
    "rename": TavernCommandEntry(
        handler="_rename",
        help_lines=["/rp rename <name>"],
    ),
    "archive": TavernCommandEntry(
        handler="_archive",
        help_lines=["/rp archive"],
        needs_command=False,
    ),
    "clone": TavernCommandEntry(
        handler="_clone",
        help_lines=["/rp clone [name]"],
    ),
    "export": TavernCommandEntry(
        handler="_export",
        help_lines=["/rp export [markdown|st-json]"],
    ),
    # ── assets ──
    "assets": TavernCommandEntry(
        handler="_assets",
        help_lines=["/rp assets"],
        needs_command=False,
    ),
    "cards": TavernCommandEntry(
        handler="_cards",
        help_lines=["/rp cards"],
        needs_event=False,
    ),
    "card": TavernCommandEntry(
        handler="_card_command",
        help_lines=[
            "/rp card import <file>",
            "/rp card search <query>",
            "/rp card inspect <card>",
            "/rp card export <card>",
            "/rp card use <card>",
            "/rp card greeting <card>",
        ],
    ),
    # ── debug ──
    "debug": TavernCommandEntry(
        handler="_debug_command",
        help_lines=[
            "/rp debug prompt [limit] [page]",
            "/rp debug context [limit] [page]",
            "/rp debug swipes",
        ],
    ),
    # ── model ──
    "model": TavernCommandEntry(
        handler="_model_command",
        help_lines=[
            "/rp model status",
            "/rp model profiles",
            "/rp model seed apiyi",
            "/rp model use <profile>",
            "/rp model mode [fake|hermes]",
            "/rp model live [status|confirm|off]",
            "/rp model test",
        ],
    ),
    # ── preset ──
    "preset": TavernCommandEntry(
        handler="_preset_command",
        help_lines=[
            "/rp preset import [file]",
            "/rp preset list",
            "/rp preset inspect <preset>",
            "/rp preset use <preset>",
            "/rp preset export <preset>",
            "/rp preset clear",
        ],
    ),
    "prompt": TavernCommandEntry(
        handler="_prompt_command",
        help_lines=[
            "/rp prompt list",
            "/rp prompt inspect <module>",
            "/rp prompt enable <module>",
            "/rp prompt disable <module>",
            "/rp prompt debug",
        ],
    ),
    # ── lorebook ──
    "lore": TavernCommandEntry(
        handler="_lore_command",
        help_lines=[
            "/rp lore import [file]",
            "/rp lore list",
            "/rp lore inspect <lorebook>",
            "/rp lore use <lorebook>",
            "/rp lore clear",
            "/rp lore export <lorebook>",
            "/rp lore enable <entry>",
            "/rp lore disable <entry>",
            "/rp lore test <message>",
            "/rp lore debug",
        ],
    ),
    # ── memory ──
    "memory": TavernCommandEntry(
        handler="_memory_command",
        help_lines=[
            "/rp memory add <fact>",
            "/rp memory forget <fact-id|all>",
            "/rp memory list [limit] [page]",
            "/rp memory summary [set <text>|clear|summarize [limit] [live]]",
            "/rp memory debug",
        ],
    ),
    # ── persona ──
    "persona": TavernCommandEntry(
        handler="_persona_command",
        help_lines=[
            "/rp persona import [file]",
            "/rp persona new <name> <text>",
            "/rp persona list [limit] [page]",
            "/rp persona inspect <persona>",
            "/rp persona use <persona>",
            "/rp persona export <persona>",
            "/rp persona temp <text>",
            "/rp persona clear",
            "/rp persona debug",
        ],
    ),
    # ── author note ──
    "note": TavernCommandEntry(
        handler="_note_command",
        help_lines=[
            "/rp note set <text>",
            "/rp note clear",
            "/rp note inspect",
            "/rp note position [before_char|after_history|before_user]",
            "/rp note frequency [always|every_n [n]]",
        ],
    ),
    # ── content mode ──
    "content": TavernCommandEntry(
        handler="_content_command",
        help_lines=["/rp content mode [safe|adult-fiction]"],
    ),
    # ── images ──
    "image": TavernCommandEntry(
        handler="_image_command",
        help_lines=[
            "/rp image [scene|character|face|background|last]",
            "/rp image prompt <text>",
            "/rp image retry",
            "/rp image inspect",
            "/rp image history [limit] [page]",
            "/rp image provider [list|status|use <name> [model]]",
            "/rp image settings [set <key> <value>|clear <key|all>]",
            "/rp image style [list|save <name>|use <name>|inspect <name>|delete <name>]",
            "/rp image safety [inspect|mode <safe|mature|explicit>|clear]",
        ],
    ),
    # ── novel layer ──
    "binding": TavernCommandEntry(
        handler="_binding_command",
        help_lines=[
            "/rp binding set <project|chapter|scene> <scope-id> <card|preset|lorebook|persona> <asset-id>",
            "/rp binding list <project|chapter|scene> <scope-id>",
            "/rp binding inspect <binding-id>",
            "/rp binding clear <binding-id>",
            "/rp binding rows are metadata-only/inert; not auto-applied",
        ],
    ),
    "style": TavernCommandEntry(
        handler="_style_command",
        help_lines=[
            "/rp style sample add <project-id> <label> <sample...>",
            "/rp style sample list [project-id]",
            "/rp style sample inspect <style-sample-id>",
            "/rp style sample update <style-sample-id> <sample...>",
            "/rp style sample delete <style-sample-id>",
        ],
    ),
    "character": TavernCommandEntry(
        handler="_character_command",
        help_lines=[
            "/rp character state add <project-id> <label> <state...>",
            "/rp character state list [project-id]",
            "/rp character state inspect <character-state-id>",
            "/rp character state update <character-state-id> <state...>",
            "/rp character state delete <character-state-id>",
        ],
    ),
    "relationship": TavernCommandEntry(
        handler="_relationship_command",
        help_lines=[
            "/rp relationship add <project-id> <label> <state...>",
            "/rp relationship list [project-id]",
            "/rp relationship inspect <relationship-id>",
            "/rp relationship rename <relationship-id> <label>",
            "/rp relationship update <relationship-id> <state...>",
            "/rp relationship delete <relationship-id>",
        ],
    ),
    "location": TavernCommandEntry(
        handler="_location_command",
        help_lines=[
            "/rp location add <project-id> <label> <description...>",
            "/rp location list [project-id]",
            "/rp location inspect <location-id>",
            "/rp location update <location-id> <description...>",
            "/rp location delete <location-id>",
        ],
    ),
    "organization": TavernCommandEntry(
        handler="_organization_command",
        help_lines=[
            "/rp organization add <project-id> <label> <description...>",
            "/rp organization list [project-id]",
            "/rp organization inspect <organization-id>",
            "/rp organization update <organization-id> <description...>",
            "/rp organization delete <organization-id>",
        ],
    ),
    "plot": TavernCommandEntry(
        handler="_plot_command",
        help_lines=[
            "/rp plot thread add <project-id> <label> <description...>",
            "/rp plot thread list [project-id]",
            "/rp plot thread inspect <plot-thread-id>",
            "/rp plot thread update <plot-thread-id> <description...>",
            "/rp plot thread delete <plot-thread-id>",
        ],
    ),
    "project": TavernCommandEntry(
        handler="_project_command",
        help_lines=[
            "/rp project create <title>",
            "/rp project list",
            "/rp project info <id>",
            "/rp project inspect <project-id>",
            "/rp project set <id>",
            "/rp project export [id]",
            "/rp project style",
            "/rp project style inspect [project-id]",
            "/rp project style set [project-id] <text>",
            "/rp project style clear [project-id]",
            "/rp project brief [project-id]",
            "/rp project brief inspect [project-id]",
            "/rp project brief type set <project-id> <novel|serial|rp|worldbuilding|other>",
            "/rp project brief type clear <project-id>",
            "/rp project brief premise set <project-id> <text>",
            "/rp project brief premise clear <project-id>",
            "/rp project outline [project-id]",
            "/rp project outline inspect [project-id]",
            "/rp project outline set [project-id] <text>",
            "/rp project outline clear [project-id]",
            "/rp project revision add <project-id> <label> <note...>",
            "/rp project revision list [project-id]",
            "/rp project revision inspect <note-id>",
            "/rp project revision update <note-id> <note...>",
            "/rp project revision delete <note-id>",
        ],
    ),
    "chapter": TavernCommandEntry(
        handler="_chapter_command",
        help_lines=[
            "/rp chapter create [project-id] <title>",
            "/rp chapter list [project-id]",
            "/rp chapter inspect <chapter-id>",
            "/rp chapter summary <chapter-id> [text]",
            "/rp chapter summary clear <chapter-id>",
        ],
    ),
    "scene": TavernCommandEntry(
        handler="_scene_command",
        help_lines=[
            "/rp scene create <chapter-id> <title>",
            "/rp scene list <chapter-id>",
            "/rp scene inspect <scene-id>",
            "/rp scene start <scene-id>",
            "/rp scene goal <scene-id> [text]",
            "/rp scene goal clear <scene-id>",
            "/rp scene beat add <scene-id> <label> <beat...>",
            "/rp scene beat list <scene-id>",
            "/rp scene beat inspect <beat-id>",
            "/rp scene beat update <beat-id> <beat...>",
            "/rp scene beat delete <beat-id>",
            "/rp scene summary <scene-id> [text]",
            "/rp scene summary clear <scene-id>",
            "/rp scene narration <scene-id>",
            "/rp scene narration clear <scene-id>",
            "/rp scene narration pov <scene-id> <label>",
            "/rp scene narration tense <scene-id> <past|present>",
        ],
    ),
    "canon": TavernCommandEntry(
        handler="_canon_command",
        help_lines=[
            "/rp canon add <project-id> <title> <content...> [--group <group>]",
            "/rp canon list [project-id] [group]",
            "/rp canon inspect <canon-id>",
            "/rp canon group [project-id] <group>",
        ],
    ),
    "timeline": TavernCommandEntry(
        handler="_timeline_command",
        help_lines=[
            "/rp timeline add <project-id> <date> <title> [description...]",
            "/rp timeline list [project-id]",
            "/rp timeline inspect <timeline-id>",
        ],
    ),
}


def _build_help_text() -> str:
    """Build /rp help output from TAVERN_COMMAND_TABLE."""
    lines = ["Hermes Tavern commands:"]
    for entry in TAVERN_COMMAND_TABLE.values():
        for hl in entry.help_lines:
            lines.append(hl)
    return "\n".join(lines)


def dispatch_command(table: dict[str, TavernCommandEntry], runtime: object, command: RPCommand, event: object) -> str:
    """Resolve and call the handler for *command* using *table* on *runtime*.

    Returns the handler's string result, or an error message for unknown commands.
    """
    entry = table.get(command.name.lower())
    if entry is None:
        from hermes_tavern.runtime_utils import mobile_preview

        return f"Unknown /rp command: {mobile_preview(command.name, 80)}"
    if not entry.handler:
        # handler="" means special — currently only "help"
        return _build_help_text()

    handler = getattr(runtime, entry.handler)
    args: list[object] = []
    if entry.needs_command:
        args.append(command)
    if entry.needs_event:
        args.append(event)
    return handler(*args)


def parse_rp_command(text: str) -> RPCommand | None:
    """Parse a `/rp` command into a small immutable command object."""
    raw = text.strip()
    parts = raw.split()
    if not parts or parts[0] != "/rp":
        return None

    if len(parts) == 1:
        return RPCommand(name="help", args=[], raw=raw)

    return RPCommand(name=parts[1].lower(), args=parts[2:], raw=raw)

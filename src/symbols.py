# Keypirinha launcher (keypirinha.com)

import keypirinha as kp
import keypirinha_util as kpu
import keypirinha_net as kpnet
import json


class Symbol:
    """
    Symbol class that holds all the data for one symbol
    """
    __slots__ = ("symbol", "name", "unicode", "hexCode", "htmlCode",
                 "htmlEntity", "cssCode", "asciiCode", "keywords")

    def __init__(self,  *initial_data, **kwargs):
        for dictionary in initial_data:
            for key in dictionary:
                keyParts = key.split("-")
                attr = keyParts[0]
                if len(keyParts) > 1:
                    for part in key.split("-")[1:]:
                        attr += part.capitalize()
                setattr(self, attr, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

class Symbols(kp.Plugin):
    """
    Copy symbol values to your clipboard
    """

    ITEM_LABEL_PREFIX = "Symbol: "
    ITEMCAT_RESULT = kp.ItemCategory.USER_BASE + 1

    def __init__(self):
        super().__init__()
        self.symbols = {}

    def initialize_symbols(self):
        """
        Parse all the symbols from the .json file
        These symbols were scraped automatically from https://www.toptal.com/designers/htmlarrows/
        """
        try:
            lines = self.load_text_resource('symbols.json')
            data = json.loads(lines)
        except Exception as exc:
            self.err("Failed to load symbols.json. Error: {}".format(exc))
            return

        for symbol, value in data.items():
            self.symbols[symbol] = Symbol(value, symbol=symbol)

    def on_start(self):
        settings = self.load_settings()
        self._displayItemsInRoot = settings.get_bool("display_items_in_root", "main", False)
        print("Display items in root [{}]".format(self._displayItemsInRoot))
        self.initialize_symbols()

    def on_catalog(self):
        catalog = []

        if self._displayItemsInRoot:
            for symbol in self.symbols.values():
                catalog.append(self.create_item(
                    category=kp.ItemCategory.KEYWORD,
                    label="{} {} {}".format(
                        self.ITEM_LABEL_PREFIX, symbol.name, symbol.symbol),
                    short_desc="Copy {}".format(symbol.symbol),
                    target="{},{}".format("copysymbol", symbol.symbol),
                    args_hint=kp.ItemArgsHint.ACCEPTED,
                    hit_hint=kp.ItemHitHint.NOARGS))
        else:
            catalog.append(self.create_item(
                category=kp.ItemCategory.REFERENCE,
                label=self.ITEM_LABEL_PREFIX,
                short_desc="Search through all symbols",
                target=self.ITEM_LABEL_PREFIX,
                args_hint=kp.ItemArgsHint.REQUIRED,
                hit_hint=kp.ItemHitHint.NOARGS))

        self.set_catalog(catalog)

    def on_suggest(self, user_input, items_chain):
        """
        List all the available symbols or the different option if a symbol item has been selected.
        """
        # If the user types symbol or smbl, set all the available symbols as suggestions
        if not items_chain:
            if (user_input.lower().startswith(("symbol", "smbl"))):
                suggestions = []

                for symbol in self.symbols.values():
                    suggestions.append(self.create_item(
                        category=kp.ItemCategory.KEYWORD,
                        label="{} {} {}".format(
                            self.ITEM_LABEL_PREFIX, symbol.name, symbol.symbol),
                        short_desc="Copy {}. Press tab for more options".format(symbol.symbol),
                        target="{},{}".format("copysymbol", symbol.symbol),
                        args_hint=kp.ItemArgsHint.ACCEPTED,
                        hit_hint=kp.ItemHitHint.NOARGS))

                self.set_suggestions(suggestions)
            return

        current_item = items_chain[-1]

        # If the user has the "Symbols:" item selected
        if current_item.target() == self.ITEM_LABEL_PREFIX:
            suggestions = []

            for symbol in self.symbols.values():
                suggestions.append(self.create_item(
                    category=kp.ItemCategory.KEYWORD,
                    label="{} {} {}".format(
                        self.ITEM_LABEL_PREFIX, symbol.name, symbol.symbol),
                    short_desc="Copy {}".format(symbol.symbol),
                    target="{},{}".format("copysymbol", symbol.symbol),
                    args_hint=kp.ItemArgsHint.ACCEPTED,
                    hit_hint=kp.ItemHitHint.NOARGS))

            self.set_suggestions(suggestions)

        # If the user has a symbol item selected
        else:
            # Extract symbol from item
            symbolKey = current_item.target().split(',', maxsplit=1)[-1]
            symbol = self.symbols[symbolKey]

            # Create the suggestions for the current item
            suggestions = []

            suggestions.append(self.create_item(
                category=self.ITEMCAT_RESULT,
                label="Copy",
                short_desc="Copy {}".format(symbol.symbol),
                target="{},{}".format("copysymbol", symbol.symbol),
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.IGNORE))

            suggestions.append(self.create_item(
                category=self.ITEMCAT_RESULT,
                label="Copy Unicode",
                short_desc="Copy {}".format(symbol.unicode),
                target="{},{}".format("copysymbol", symbol.unicode),
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.IGNORE))

            suggestions.append(self.create_item(
                category=self.ITEMCAT_RESULT,
                label="Copy HEX Code",
                short_desc="Copy {}".format(symbol.hexCode),
                target="{},{}".format("copysymbol", symbol.hexCode),
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.IGNORE))

            suggestions.append(self.create_item(
                category=self.ITEMCAT_RESULT,
                label="Copy HTML Code",
                short_desc="Copy {}".format(symbol.htmlCode),
                target="{},{}".format("copysymbol", symbol.htmlCode),
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.IGNORE))

            suggestions.append(self.create_item(
                category=self.ITEMCAT_RESULT,
                label="Copy HTML Entity",
                short_desc="Copy {}".format(symbol.htmlEntity),
                target="{},{}".format(
                    "copysymbol", symbol.htmlEntity),
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.IGNORE))

            suggestions.append(self.create_item(
                category=self.ITEMCAT_RESULT,
                label="Copy CSS Code",
                short_desc="Copy {}".format(symbol.cssCode),
                target="{},{}".format("copysymbol", symbol.cssCode),
                args_hint=kp.ItemArgsHint.FORBIDDEN,
                hit_hint=kp.ItemHitHint.IGNORE))

            self.set_suggestions(suggestions, kp.Match.FUZZY, kp.Sort.NONE)

        return

    def on_execute(self, item, action):
        """
        Exeute the given item
        """
        print("Executing item [{}] of type [{}], category [{}] and target [{}]".format(item, type(item), item.category(), item.target()))

        # Extract and copy the value
        value = item.target().split(',', maxsplit=1)[-1]
        print("Copying symbol to clipboard [{}]".format(value))
        kpu.set_clipboard(value)

    def on_activated(self):
        pass

    def on_deactivated(self):
        pass

    def on_events(self, flags):
        pass
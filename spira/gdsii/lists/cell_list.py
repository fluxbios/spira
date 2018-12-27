from spira.gdsii.cell import Cell
from spira.param.field.typed_list import TypedList
class CellList(TypedList):

    __item_type__ = Cell

    def is_empty(self):
        if (len(self._list) == 0): return True
        for e in self._list:
            if not e.is_empty(): return False
        return True

    def __getitem__(self, key):
        if isinstance(key, str):
            for i in self._list:
                if i.name == key: return i
            raise IndexError("Structure " + key + " cannot be found in StructureList.")
        else:
            return list.__getitem__(self._list, key)

    def __setitem__(self, key, value):
        if isinstance(key, str):
            for i in range(0, len(self._list)):
                if self._list[i].name == key: 
                    return list.__setitem__(self._list, i, value)
            list.append(self._list, value)
        else:
            return list.__setitem__(self._list, key, value)

    def __delitem__(self, key):
        if isinstance(key, str):
            for i in range(0, len(self._list)):
                if self._list[i].name == key: 
                    return list.__delitem__(self._list, i)
                return
            return list.__delitem__(self._list, key)
        else:
            return list.__delitem__(self._list, key)

    def __contains__(self, item):
        if isinstance(item, Cell):
            name = item.name
        else:
            name = item
        if isinstance(name, str):
            for i in self._list:
                if i.name == name: return True
            return False
        else:
            return list.__contains__(self._list, item)

    def __fast_contains__(self, name):
        for i in self._list:
            if i.name == name:
                return True
        return False

    def index(self, item):
        if isinstance(item, str):
            for i in range(0, len(self._list)):
                if list.__getitem__(self._list, i).name == item:
                    return i
            raise ValueError("Cell " + item + " is not in CellList")
        else:
            list.index(self._list, item)

    def add(self, item, overwrite=False):
        if item == None:
            return
        if isinstance(item, Cell):
            if overwrite:
                self._list[item.name] = item
                return
            elif not self.__fast_contains__(item.name):
                self._list.append(item)
        elif isinstance(item, (CellList, list, set)):
            for s in item:
                self.add(s, overwrite)
        else:
            raise ValueError('Cannot add cell!')

    def append(self, other, overwrite = False):
        return self.add(other, overwrite)

    def extend(self, other, overwrite = False):
        return self.add(other, overwrite)
# -- coding: utf-8 --

class Rect(object):
    def __init__(self, top, right, bottom, left) -> None:
        super().__init__()
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left

    def __str__(self) -> str:
        return "top:{},right:{},bottom:{},left:{}".format(self.top, self.right, self.bottom, self.left)

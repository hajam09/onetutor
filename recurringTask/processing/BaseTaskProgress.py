class BaseTaskProgress:

    def __init__(self, total):
        self.total = total
        self.currentProgress = 0

    def addProgress(self, progress):
        self.setProgress(self.currentProgress + progress)

    def setProgress(self, progress):
        self.currentProgress = progress

        if self.currentProgress > self.total:
            self.currentProgress = self.total

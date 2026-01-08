# Copyright (c) 2025, thanhnc and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class APSRLTrainingLog(Document):
    def before_save(self):
        """Calculate progress percentage before save."""
        if self.max_episodes and self.current_episode:
            self.progress_percentage = (self.current_episode / self.max_episodes) * 100

class Sync:
    run_core = False
    
    @classmethod
    def get_flag(cls):
        return cls.run_core
    
    @classmethod
    def set_flag(cls):
        cls.run_core = True
    
    @classmethod
    def clear_flag(cls):
        cls.run_core = False
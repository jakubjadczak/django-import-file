# Save log into database
from abc import ABC, abstractmethod


class LogTypeWriterStrategy(ABC):
    @abstractmethod
    def write_log(self, model, app_name: str, operation_status: str, **kwargs):
        pass


class SimpleLogWriter(LogTypeWriterStrategy):
    
    def write_log(self, model, app_name: str, operation_status: str, **kwargs):
        """ 
        Required db structure:

        app_name: CharField
        operataion_status: CharField
        rows_amount: IntegerField
        timestamp: DateTimeField(auto_created=True)
        """
        try:
            model.create(
                app_name=app_name,
                operation_status=operation_status,
                rows_amount=kwargs["rows_amount"],
            )
            return "200"
        except Exception as err:
            return err
        

class ExtendedLogWriter(LogTypeWriterStrategy):

    def write_log(self, model, app_name: str, operation_status: str, **kwargs):
        pass


class LogConfig:
    _instance = None

    def __new__(cls, model, app_name: str, log_type: str):
        if cls._instance is None:
            cls._instance = super(LogConfig, cls).__new__(cls)
            cls._instance._initialize(model, app_name, log_type)
        return cls._instance
    
    def _initialize(self, model, app_name: str, log_type: str):
        self.model = model
        self.app_name = app_name
        self.log_type = log_type
        self.log_type_dict = {
            "simple": SimpleLogWriter(),
            "extended": ExtendedLogWriter()
        }

        return self # method chaining

    def write_log(self, **kwargs):
        if self.log_type == "simple":
            return self.log_type_dict["simple"].write_log(self.model, self.app_name, rows_amount=kwargs["rows_amount"])
        
        elif self.log_type == "extended":
            return self.log_type_dict["simple"].write_log(self.model, self.app_name, rows_amount=kwargs["rows_amount"], messages=kwargs["messages"])
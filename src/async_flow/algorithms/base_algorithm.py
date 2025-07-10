class BaseAlgorithm:
    def select_server(self, server_list):

        """
        :param server_list: List of available servers.
        Select a server based on the algorithm.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")



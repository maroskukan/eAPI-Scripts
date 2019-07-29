from configparser import ConfigParser


def read_config(filename='config.ini', section='network-api'):
    """ Reads configuration file and returns a dictionary object
    :param filename: name of the configuration file
    :param section: section of configuration
    :return: a dictionary of parameters
    """
    # create parser and read ini configuration file
    parser = ConfigParser()
    parser.read(filename)
 
    # get section, default to network
    config = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            config[item[0]] = item[1]
    else:
        raise Exception('{0} not found in the {1} file'.format(section, filename))
 
    return config
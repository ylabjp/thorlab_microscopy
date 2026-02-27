from datetime import datetime, timedelta
from bioio import StandardMetadata


class ThorlabXMLtoStandardMetadata:
    """
    Convert Thorlabs Experiment.xml into BioIO StandardMetadata.
    """

    def __init__(self, parsed_xml: dict):
        self.xml = parsed_xml

    def convert(self) -> StandardMetadata:
        return StandardMetadata(
            image_size_x=self.xml.get("SizeX"),
            image_size_y=self.xml.get("SizeY"),
            image_size_z=self.xml.get("SizeZ"),
            image_size_c=self.xml.get("SizeC"),
            image_size_t=self.xml.get("SizeT"),

            pixel_size_x=self.xml.get("PhysicalSizeX"),
            pixel_size_y=self.xml.get("PhysicalSizeY"),
            pixel_size_z=self.xml.get("PhysicalSizeZ"),

            objective=self.xml.get("Objective"),
            imaged_by="Thorlab Microscope",

            timelapse=self.xml.get("SizeT", 1) > 1,
        )


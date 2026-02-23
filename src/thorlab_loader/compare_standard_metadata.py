from bioio import StandardMetadata


class StandardMetadataComparator:
    def __init__(self, bio: StandardMetadata, xml: StandardMetadata):
        self.bio = bio
        self.xml = xml

    def compare(self) -> list[str]:
        errors = []

        def check(field):
            if getattr(self.bio, field) != getattr(self.xml, field):
                errors.append(
                    f"{field}: {getattr(self.bio, field)} != {getattr(self.xml, field)}"
                )

        fields = [
            "image_size_x",
            "image_size_y",
            "image_size_z",
            "image_size_c",
            "image_size_t",
            "pixel_size_x",
            "pixel_size_y",
            "pixel_size_z",
        ]

        for f in fields:
            check(f)

        return errors


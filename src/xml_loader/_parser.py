from __future__ import annotations

import xml.sax
from typing import Callable, List, Optional, Tuple, Dict, Any
from xml.sax.xmlreader import AttributesNSImpl

NAMESPACES = {
    "oai": "http://www.openarchives.org/OAI/2.0/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "dcndl": "http://ndl.go.jp/dcndl/terms/",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "owl": "http://www.w3.org/2002/07/owl#",
    "foaf": "http://xmlns.com/foaf/0.1/",
}


class _DcndlSaxHandler(xml.sax.ContentHandler):
    def __init__(self, record_callback: Callable[[Dict[str, Any]], None]) -> None:
        super().__init__()
        self.record_callback = record_callback
        self._path: List[str] = []
        self._current_text: str = ""
        self._current_record_dict: Optional[Dict[str, Any]] = None
        self._current_attributes: AttributesNSImpl = AttributesNSImpl({}, {})

    def startElementNS(
        self,
        name: Tuple[Optional[str], str],
        qname: Optional[str],
        attrs: AttributesNSImpl,
    ) -> None:
        ns_uri, localname = name
        self._path.append(localname)
        self._current_text = ""
        self._current_attributes = attrs

        if localname == "record" and ns_uri == NAMESPACES["oai"]:
            self._current_record_dict = {"header": {}, "metadata": {"dc": {}}}

    def endElementNS(
        self, name: Tuple[Optional[str], str], qname: Optional[str]
    ) -> None:
        ns_uri, localname = name

        if not self._current_record_dict:
            self._path.pop()
            return

        if localname == "record" and ns_uri == NAMESPACES["oai"]:
            self.record_callback(self._current_record_dict)
            self._current_record_dict = None

        elif localname == "identifier" and ns_uri == NAMESPACES["oai"]:
            self._current_record_dict["header"]["identifier"] = self._current_text
            # Also add it to the dc:identifier list for consistency
            dc_dict = self._current_record_dict["metadata"]["dc"]
            dc_dict.setdefault("identifier", []).append({"value": self._current_text, "type": "dcterms:URI"})
        elif localname == "datestamp" and ns_uri == NAMESPACES["oai"]:
            self._current_record_dict["header"]["datestamp"] = self._current_text

        elif "dc" in self._current_record_dict["metadata"]:
            dc_dict = self._current_record_dict["metadata"]["dc"]

            # --- Simple text fields (last one wins) ---
            simple_fields = {
                (NAMESPACES["dc"], "title"): "title",
                (NAMESPACES["dc"], "publisher"): "publisher",
                (NAMESPACES["dcterms"], "alternative"): "alternative",
                (NAMESPACES["dcndl"], "seriesTitle"): "series_title",
                (NAMESPACES["dc"], "date"): "date",
                (NAMESPACES["dc"], "language"): "language",
                (NAMESPACES["dcterms"], "extent"): "extent",
                (NAMESPACES["dcndl"], "materialType"): "material_type",
                (NAMESPACES["dcterms"], "accessRights"): "access_rights",
                (NAMESPACES["dcndl"], "titleTranscription"): "title_transcription",
                (NAMESPACES["dcndl"], "volume"): "volume",
            }
            if ns_uri is not None and (ns_uri, localname) in simple_fields:
                field_key = simple_fields[(ns_uri, localname)]
                dc_dict[field_key] = self._current_text

            # --- List fields ---
            elif (ns_uri, localname) == (NAMESPACES["dc"], "creator"):
                dc_dict.setdefault("creator", []).append(self._current_text)

            # --- Complex fields ---
            elif localname == "identifier" and ns_uri == NAMESPACES["dc"]:
                type_attr = self._current_attributes.get((NAMESPACES["xsi"], "type"))
                dc_dict.setdefault("identifier", []).append(
                    {"value": self._current_text, "type": type_attr}
                )
            elif localname == "publicationPlace" and ns_uri == NAMESPACES["dcndl"]:
                type_attr = self._current_attributes.get((NAMESPACES["xsi"], "type"))
                dc_dict.setdefault("publication_place", []).append(
                    {"value": self._current_text, "type": type_attr}
                )
            elif localname == "issued" and ns_uri == NAMESPACES["dcterms"]:
                type_attr = self._current_attributes.get((NAMESPACES["xsi"], "type"))
                dc_dict.setdefault("issued", []).append(
                    {"value": self._current_text, "type": type_attr}
                )
            elif localname == "subject" and ns_uri == NAMESPACES["dc"]:
                type_attr = self._current_attributes.get((NAMESPACES["xsi"], "type"))
                dc_dict.setdefault("subject", []).append(
                    {"value": self._current_text, "type": type_attr}
                )

            # --- Resource links ---
            elif localname == "seeAlso" and ns_uri == NAMESPACES["rdfs"]:
                res_attr = self._current_attributes.get((NAMESPACES["rdf"], "resource"))
                if res_attr:
                    dc_dict.setdefault("see_also", []).append({"resource": res_attr})
            elif localname == "sameAs" and ns_uri == NAMESPACES["owl"]:
                res_attr = self._current_attributes.get((NAMESPACES["rdf"], "resource"))
                if res_attr:
                    dc_dict.setdefault("same_as", []).append({"resource": res_attr})
            elif localname == "thumbnail" and ns_uri == NAMESPACES["foaf"]:
                res_attr = self._current_attributes.get((NAMESPACES["rdf"], "resource"))
                if res_attr:
                    dc_dict.setdefault("thumbnail", []).append({"resource": res_attr})

        self._path.pop()

    def characters(self, content: str) -> None:
        self._current_text += content.strip()


def _parse_dcndl_xml(
    file_path: str, record_callback: Callable[[Dict[str, Any]], None]
) -> None:
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, True)
    handler = _DcndlSaxHandler(record_callback)
    parser.setContentHandler(handler)
    parser.parse(file_path)

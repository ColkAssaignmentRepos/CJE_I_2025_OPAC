from __future__ import annotations

import xml.sax
from typing import Callable, List, Optional, Tuple
from xml.sax.xmlreader import AttributesNSImpl

from src.xml_loader._schema import (
    _Record,
    _Header,
    _Metadata,
    _DcndlSimple,
    _TypedValue,
    _ResourceLink,
)

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
    def __init__(self, record_callback: Callable[[_Record], None]) -> None:
        super().__init__()
        self.record_callback = record_callback
        self._path: List[str] = []
        self._current_text: str = ""
        self._current_record: Optional[_Record] = None
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
            self._current_record = _Record()
        elif self._current_record:
            if localname == "header":
                self._current_record.header = _Header()
            elif localname == "metadata":
                self._current_record.metadata = _Metadata()
            elif localname == "dc" and self._current_record.metadata:
                self._current_record.metadata.dc = _DcndlSimple()

    def endElementNS(
        self, name: Tuple[Optional[str], str], qname: Optional[str]
    ) -> None:
        ns_uri, localname = name

        if not self._current_record:
            self._path.pop()
            return

        if localname == "record" and ns_uri == NAMESPACES["oai"]:
            self.record_callback(self._current_record)
            self._current_record = None

        elif self._current_record.header and not self._current_record.metadata:
            if localname == "identifier" and ns_uri == NAMESPACES["oai"]:
                self._current_record.header.identifier = self._current_text
            elif localname == "datestamp" and ns_uri == NAMESPACES["oai"]:
                self._current_record.header.datestamp = self._current_text

        elif self._current_record.metadata and self._current_record.metadata.dc:
            dc = self._current_record.metadata.dc
            if localname == "title" and ns_uri == NAMESPACES["dc"]:
                dc.title = self._current_text
            elif localname == "alternative" and ns_uri == NAMESPACES["dcterms"]:
                dc.alternative = self._current_text
            elif localname == "seriesTitle" and ns_uri == NAMESPACES["dcndl"]:
                dc.series_title = self._current_text
            elif localname == "creator" and ns_uri == NAMESPACES["dc"]:
                dc.creator.append(self._current_text)
            elif localname == "publisher" and ns_uri == NAMESPACES["dc"]:
                dc.publisher = self._current_text
            elif localname == "date" and ns_uri == NAMESPACES["dc"]:
                dc.date = self._current_text
            elif localname == "language" and ns_uri == NAMESPACES["dc"]:
                dc.language = self._current_text
            elif localname == "extent" and ns_uri == NAMESPACES["dcterms"]:
                dc.extent = self._current_text
            elif localname == "materialType" and ns_uri == NAMESPACES["dcndl"]:
                dc.material_type = self._current_text
            elif localname == "accessRights" and ns_uri == NAMESPACES["dcterms"]:
                dc.access_rights = self._current_text
            elif localname == "titleTranscription" and ns_uri == NAMESPACES["dcndl"]:
                dc.title_transcription = self._current_text
            elif localname == "volume" and ns_uri == NAMESPACES["dcndl"]:
                dc.volume = self._current_text

            elif localname == "identifier" and ns_uri == NAMESPACES["dc"]:
                type_attr = self._current_attributes.get((NAMESPACES["xsi"], "type"))
                dc.identifier.append(
                    _TypedValue(value=self._current_text, type=type_attr)
                )
            elif localname == "publicationPlace" and ns_uri == NAMESPACES["dcndl"]:
                type_attr = self._current_attributes.get((NAMESPACES["xsi"], "type"))
                dc.publication_place.append(
                    _TypedValue(value=self._current_text, type=type_attr)
                )
            elif localname == "issued" and ns_uri == NAMESPACES["dcterms"]:
                type_attr = self._current_attributes.get((NAMESPACES["xsi"], "type"))
                dc.issued.append(_TypedValue(value=self._current_text, type=type_attr))
            elif localname == "subject" and ns_uri == NAMESPACES["dc"]:
                type_attr = self._current_attributes.get((NAMESPACES["xsi"], "type"))
                dc.subject.append(_TypedValue(value=self._current_text, type=type_attr))

            elif localname == "seeAlso" and ns_uri == NAMESPACES["rdfs"]:
                res_attr = self._current_attributes.get((NAMESPACES["rdf"], "resource"))
                if res_attr:
                    dc.see_also.append(_ResourceLink(resource=res_attr))
            elif localname == "sameAs" and ns_uri == NAMESPACES["owl"]:
                res_attr = self._current_attributes.get((NAMESPACES["rdf"], "resource"))
                if res_attr:
                    dc.same_as.append(_ResourceLink(resource=res_attr))
            elif localname == "thumbnail" and ns_uri == NAMESPACES["foaf"]:
                res_attr = self._current_attributes.get((NAMESPACES["rdf"], "resource"))
                if res_attr:
                    dc.thumbnail.append(_ResourceLink(resource=res_attr))

        self._path.pop()

    def characters(self, content: str) -> None:
        self._current_text += content.strip()


def _parse_dcndl_xml(
    file_path: str, record_callback: Callable[[_Record], None]
) -> None:
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, True)
    handler = _DcndlSaxHandler(record_callback)
    parser.setContentHandler(handler)
    parser.parse(file_path)

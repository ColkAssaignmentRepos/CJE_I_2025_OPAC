import { useState, useEffect, type FormEvent } from 'react';
import axios from 'axios';
import { Modal, Button, InputGroup, Form } from 'react-bootstrap';
import { Search, Book, Person } from 'react-bootstrap-icons';

// --- (API Data Structures remain the same) ---
interface TypedValue_string_ {
    value: string;
    type?: string | null;
}
interface Header {
    identifier: string;
    datestamp: string;
}
interface DcndlSimple {
    title: string;
    identifier: TypedValue_string_[];
    creator?: string[];
    publisher?: string | null;
    alternative?: string | null;
    series_title?: string | null;
    date?: string | null;
    language?: string | null;
    extent?: string | null;
    material_type?: string | null;
    access_rights?: string | null;
    title_transcription?: string | null;
    volume?: string | null;
}
interface Metadata {
    dc: DcndlSimple;
}
interface Record {
    header: Header;
    metadata: Metadata;
}
interface PaginatedRecordResponse {
    items: Record[];
    total_items: number;
    total_pages: number;
    current_page: number;
    per_page: number;
}

const apiClient = axios.create({
    baseURL: '/api/v1',
    headers: { 'Content-Type': 'application/json' },
});

function App() {
    const [searchType, setSearchType] = useState<'any' | 'specific'>('any');
    const [query, setQuery] = useState('');
    const [title, setTitle] = useState('');
    const [creator, setCreator] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const [results, setResults] = useState<PaginatedRecordResponse | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [selectedRecord, setSelectedRecord] = useState<Record | null>(null);

    useEffect(() => {
        if (query || title || creator) fetchResults();
        else setResults(null);
    }, [currentPage]);

    const fetchResults = async () => {
        setIsLoading(true);
        setError(null);
        const params = new URLSearchParams({
            page: String(currentPage),
            per_page: '20',
        });
        if (searchType === 'any' && query) params.append('q', query);
        else {
            if (title) params.append('title', title);
            if (creator) params.append('creator', creator);
        }
        try {
            const response = await apiClient.get<PaginatedRecordResponse>('/search', { params });
            setResults(response.data);
        } catch (err) {
            setError('Failed to fetch results. Is the backend server running?');
        } finally {
            setIsLoading(false);
        }
    };

    const handleSearch = (e: FormEvent) => {
        e.preventDefault();
        setCurrentPage(1);
        fetchResults();
    };

    const handleShowDetails = (record: Record) => setSelectedRecord(record);
    const handleCloseDetails = () => setSelectedRecord(null);

    const renderPagination = () => {
        if (!results || results.total_pages <= 1) return null;
        const pageNumbers = [];
        const maxPagesToShow = 5;
        let startPage = Math.max(1, results.current_page - Math.floor(maxPagesToShow / 2));
        let endPage = Math.min(results.total_pages, startPage + maxPagesToShow - 1);
        if (endPage - startPage + 1 < maxPagesToShow) {
            startPage = Math.max(1, endPage - maxPagesToShow + 1);
        }
        for (let i = startPage; i <= endPage; i++) pageNumbers.push(i);
        return (
            <nav><ul className="pagination justify-content-center">
                <li className={`page-item ${results.current_page === 1 ? 'disabled' : ''}`}><button className="page-link" onClick={() => setCurrentPage(results.current_page - 1)}>Previous</button></li>
                {pageNumbers.map(num => (<li key={num} className={`page-item ${results.current_page === num ? 'active' : ''}`}><button className="page-link" onClick={() => setCurrentPage(num)}>{num}</button></li>))}
                <li className={`page-item ${results.current_page === results.total_pages ? 'disabled' : ''}`}><button className="page-link" onClick={() => setCurrentPage(results.current_page + 1)}>Next</button></li>
            </ul></nav>
        );
    };

    return (
        <div className="container mt-4">
            <div className="row justify-content-center">
                <div className="col-md-10 col-lg-8">
                    <div className="text-center mb-5">
                        <h1 className="display-4">OPAC Search</h1>
                        <p className="lead text-muted">Find books and publications</p>
                    </div>

                    <div className="search-card mb-5">
                        <Form onSubmit={handleSearch}>
                            <div className="mb-3">
                                <Form.Check inline label="ANY Search" name="searchType" type="radio" id="any-radio" value="any" checked={searchType === 'any'} onChange={() => setSearchType('any')} />
                                <Form.Check inline label="Specific Fields" name="searchType" type="radio" id="specific-radio" value="specific" checked={searchType === 'specific'} onChange={() => setSearchType('specific')} />
                            </div>
                            {searchType === 'any' ? (
                                <InputGroup className="mb-3">
                                    <Form.Control size="lg" placeholder="Search title and creator..." value={query} onChange={e => setQuery(e.target.value)} />
                                    <Button type="submit" variant="primary" disabled={isLoading}><Search className="me-2"/>Search</Button>
                                </InputGroup>
                            ) : (
                                <>
                                    <InputGroup className="mb-3">
                                        <InputGroup.Text><Book /></InputGroup.Text>
                                        <Form.Control size="lg" placeholder="Title..." value={title} onChange={e => setTitle(e.target.value)} />
                                    </InputGroup>
                                    <InputGroup className="mb-3">
                                        <InputGroup.Text><Person /></InputGroup.Text>
                                        <Form.Control size="lg" placeholder="Creator..." value={creator} onChange={e => setCreator(e.target.value)} />
                                    </InputGroup>
                                    <Button type="submit" variant="primary" className="w-100" disabled={isLoading}><Search className="me-2"/>Search</Button>
                                </>
                            )}
                        </Form>
                    </div>

                    {isLoading && <div className="text-center"><div className="spinner-border" role="status"><span className="visually-hidden">Loading...</span></div></div>}
                    {error && <div className="alert alert-danger">{error}</div>}
                    
                    {results && (
                        results.items.length > 0 ? (
                            <div>
                                <p className="text-center text-muted mb-4">Found {results.total_items} results. Page {results.current_page} of {results.total_pages}.</p>
                                <div>
                                    {results.items.map(record => (
                                        <div key={record.header.identifier} className="result-item" onClick={() => handleShowDetails(record)}>
                                            <h5 className="mb-1">{record.metadata.dc.title}</h5>
                                            <p className="mb-1 text-muted">{record.metadata.dc.creator?.join(', ')}</p>
                                            <small>Publisher: {record.metadata.dc.publisher || 'N/A'}</small>
                                        </div>
                                    ))}
                                </div>
                                <div className="mt-4">{renderPagination()}</div>
                            </div>
                        ) : (
                            <div className="text-center text-muted mt-5">
                                <h4>No Results Found</h4>
                                <p>Try adjusting your search terms.</p>
                            </div>
                        )
                    )}
                </div>
            </div>

            {selectedRecord && (
                <Modal show={true} onHide={handleCloseDetails} size="lg" centered>
                    <Modal.Header closeButton><Modal.Title>{selectedRecord.metadata.dc.title}</Modal.Title></Modal.Header>
                    <Modal.Body>
                        <h6>Creators</h6><p>{selectedRecord.metadata.dc.creator?.join(', ') || 'N/A'}</p>
                        <h6>Publisher</h6><p>{selectedRecord.metadata.dc.publisher || 'N/A'}</p>
                        <h6>Publication Date</h6><p>{selectedRecord.metadata.dc.date || 'N/A'}</p>
                        <h6>Identifiers</h6>
                        <ul>{selectedRecord.metadata.dc.identifier.map((id, index) => (<li key={index}><strong>{id.type || 'ID'}:</strong> {id.value}</li>))}</ul>
                        <h6>Additional Info</h6>
                        <dl className="row">
                            <dt className="col-sm-4">Alternative Title</dt><dd className="col-sm-8">{selectedRecord.metadata.dc.alternative || 'N/A'}</dd>
                            <dt className="col-sm-4">Series Title</dt><dd className="col-sm-8">{selectedRecord.metadata.dc.series_title || 'N/A'}</dd>
                            <dt className="col-sm-4">Language</dt><dd className="col-sm-8">{selectedRecord.metadata.dc.language || 'N/A'}</dd>
                            <dt className="col-sm-4">Extent</dt><dd className="col-sm-8">{selectedRecord.metadata.dc.extent || 'N/A'}</dd>
                            <dt className="col-sm-4">Material Type</dt><dd className="col-sm-8">{selectedRecord.metadata.dc.material_type || 'N/A'}</dd>
                        </dl>
                    </Modal.Body>
                    <Modal.Footer><Button variant="secondary" onClick={handleCloseDetails}>Close</Button></Modal.Footer>
                </Modal>
            )}
        </div>
    );
}

export default App;